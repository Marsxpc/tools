import os,sys,shutil,glob,threading
from PIL import Image
from PyQt5.QtWidgets import QFileDialog,QLineEdit,QVBoxLayout,QPushButton,QGridLayout,QLabel,QTreeWidget,QTreeWidgetItem,QTabWidget,QListWidget,QApplication, QMenu, QWidget,QTreeWidgetItemIterator
from PyQt5.QtGui import QIcon,QPixmap,QCursor,QBrush,QImage
from PyQt5.QtCore import Qt,QSize,QFile
import resource


class UiDialog(QWidget):
    def __init__(self,parent=None):
        super(UiDialog, self).__init__(parent)
        layout_dialog = QVBoxLayout()
        self.filename_edit = QLineEdit()
        self.btn_confirm = QPushButton("确认")
        self.btn_cancel = QPushButton("取消")
        layout_dialog.addWidget(self.filename_edit)
        layout_dialog.addWidget(self.btn_confirm)
        layout_dialog.addWidget(self.btn_cancel)
        self.setLayout(layout_dialog)


class WindowClass(QTabWidget):
    def __init__(self,parent=None):
        super(WindowClass, self).__init__(parent)
        # self.resize(781, 508)
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        # 将选项卡添加到顶层窗口中
        self.addTab(self.tab1, "目录比对")
        self.tab1UI()
        self.tab2UI()
        self.setWindowTitle("查图工具")

    def tab1UI(self):
        # 网格布局
        grid_layout = QGridLayout()
        self.log_info = QListWidget()
        self.log_info.setMaximumHeight(100)
        self.btn_rename_all = QPushButton("一键重命名")
        self.btn_rename_all.clicked.connect(self.renameAll)

        self.treeA = QTreeWidget()
        self.treeA.setColumnCount(1)
        self.treeA.setHeaderLabels(['Name'])
        self.treeA.setColumnWidth(0, 150)
        self.treeA.clicked.connect(lambda: self.addInfo('count',self.treeA.currentItem(),self.filename_editA))
        self.treeA.doubleClicked.connect(lambda: self.showImage(self.treeA.currentItem(),self.filename_editA,self.filename_editB))
        self.treeA.doubleClicked.connect(
            lambda: self.showImage(self.treeA.currentItem(), self.filename_editA, self.filename_editB))
        self.treeB = QTreeWidget()
        self.treeB.setColumnCount(1)
        self.treeB.setHeaderLabels(['Name'])
        self.treeB.setColumnWidth(0, 150)
        self.treeB.clicked.connect(lambda: self.addInfo('count', self.treeB.currentItem(), self.filename_editB))
        self.treeB.doubleClicked.connect(lambda: self.showImage(self.treeB.currentItem(),self.filename_editA,self.filename_editB))
        self.treeB.doubleClicked.connect(
            lambda: self.showImage(self.treeB.currentItem(), self.filename_editA, self.filename_editB))
        self.filename_editA = QLineEdit()
        self.filename_editA.setPlaceholderText("路径选择")
        self.btn_loadA = QPushButton("浏览")
        self.btn_loadA.clicked.connect(lambda : self.setDir(self.filename_editA))
        self.btn_loadA.clicked.connect(lambda: self.loadDir(onlyload=False))
        self.btn_refresh = QPushButton("刷新")
        self.btn_refresh.clicked.connect(lambda: self.loadDir(onlyload=False))

        self.filename_editB = QLineEdit()
        self.filename_editB.setPlaceholderText("路径选择")
        self.btn_loadB = QPushButton("浏览")
        self.btn_loadB.clicked.connect(lambda : self.setDir(self.filename_editB))
        self.btn_loadB.clicked.connect(lambda: self.loadDir(onlyload=False))
        # 将控件添加到布局
        grid_layout.addWidget(self.filename_editA,1,0)
        grid_layout.addWidget(self.btn_loadA,1,1)
        grid_layout.addWidget(self.treeA,2,0,1,2)
        grid_layout.addWidget(self.filename_editB,1,2)
        grid_layout.addWidget(self.btn_loadB,1,3)
        grid_layout.addWidget(self.treeB,2,2,1,2)
        grid_layout.addWidget(self.log_info,3,0,2,3)
        grid_layout.addWidget(self.btn_rename_all, 3, 3, 1, 4)
        grid_layout.addWidget(self.btn_refresh,4,3,1,4)
        self.tab1.setLayout(grid_layout)
        # 只针对树形控件创建右键功能
        self.contextMenuA = QMenu()
        self.contextMenuB = QMenu()
        self.createContextMenu(self.treeA,self.filename_editA,self.contextMenuA)
        self.createContextMenu(self.treeB,self.filename_editB,self.contextMenuB)

    def tab2UI(self):
        gridbox = QGridLayout()
        self.next_item = None
        self.btn_pathA = QPushButton("前一张")
        self.btn_pathA.clicked.connect(lambda: self.hasBeforeItem(self.next_item))
        self.btn_pathA.clicked.connect(lambda: self.showImage(self.next_item,self.filename_editA,self.filename_editB))
        self.btn_pathB = QPushButton("后一张")
        self.btn_pathB.clicked.connect(lambda: self.hasNextItem(self.next_item))
        self.btn_pathB.clicked.connect(lambda: self.showImage(self.next_item,self.filename_editA,self.filename_editB))
        self.line_pathA = QLineEdit()
        self.line_pathB = QLineEdit()
        self.labelA = QLabel()
        self.labelB = QLabel()
        # 将控件添加到布局
        gridbox.addWidget(self.btn_pathA,1,0)
        gridbox.addWidget(self.line_pathA,1,1)
        gridbox.addWidget(self.labelA,2,0,4,2)
        gridbox.addWidget(self.btn_pathB,1,3)
        gridbox.addWidget(self.line_pathB,1,2)
        gridbox.addWidget(self.labelB,2,2,4,2)
        self.tab2.setLayout(gridbox)

    def renameAll(self):
        flag = True
        path1 = self.filename_editA.text()
        path2 = self.filename_editB.text()
        if path1 == '' or path2 == '':
            pass
        else:
            if os.path.isdir(path1) and os.path.isdir(path2):
                # 保证每一层目录下图片数量都是相等的
                if len(self.listImage(path1)) != len(self.listImage(path2)):
                    flag = False
                for root, dirs, files in os.walk(path1, topdown=False):
                    for di in dirs:
                        if len(self.listImage(os.path.join(root, di))) != \
                                len(self.listImage(os.path.join(root, di).replace(path1,path2))):
                            flag = False
                if flag:
                    self.renameImage(path1,path2)
                    for root, dirs, files in os.walk(path1, topdown=False):
                        for di in dirs:
                            self.renameImage(os.path.join(root,di), os.path.join(root,di).replace(path1,path2))
                    self.loadDir()
                else:
                    self.addInfo(u'图片数量不相等！')
                    return

    def addInfo(self,action,item=None,line_obj=None):
        info = ''
        if item:
            url = self.getItemPath(item, line_obj.text())
            if action == 'count':
                if os.path.isdir(url):
                    count = len(self.listImage(url))
                    for root, dirs, files in os.walk(url, topdown=False):
                        for di in dirs:
                            count = count + len(self.listImage(os.path.join(root, di)))
                    info = f'当前路径  {url}\n图片数为：{count}'
            elif action == 'modify':
                dst = '/'.join((os.path.dirname(url), self.uidialog.filename_edit.text()))
                info = f'改动前：{url}\n改动后：{dst}'
            elif action == 'delete':
                info = f'删除  {url}'
        else:
            info = action
        self.log_info.clear()
        self.log_info.addItem(info)

    def listImage(self,url):
        return glob.glob(f'{url}/*.png') + glob.glob(f'{url}/*.jpg')

    def renameImage(self,pathA,pathB):
        # 前者重命名后者,一键重命名使用
        pathA = pathA.replace('/','\\')
        pathB = pathB.replace('/','\\')
        if self.listImage(pathA) != []:
            for idx, one in enumerate(self.listImage(pathA)):
                try:
                    os.rename(os.path.join(pathB, os.path.split(self.listImage(pathB)[idx])[1]),
                              os.path.join(pathB, os.path.split(one)[1]))
                except (FileExistsError, FileNotFoundError):
                    pass

    def setDir(self,line_obj):
        choice_path = "D:/"
        if line_obj.text():
            choice_path = line_obj.text()
        download_path = QFileDialog.getExistingDirectory(self,"浏览",choice_path)
        line_obj.setText(download_path)

    def loadDir(self,onlyload=True):
        # 默认不清除log_info
        if not onlyload:
            self.removeTab(1)
            self.log_info.clear()
        self.qicon = QIcon(':/img/file.png')
        # 移除之前添加的节点
        self.treeA.takeTopLevelItem(0)
        self.treeB.takeTopLevelItem(0)
        base_pathA = self.filename_editA.text()
        base_pathB = self.filename_editB.text()
        if base_pathA:
            # 设置根节点
            rootA = QTreeWidgetItem(self.treeA)
            rootA.setText(0, os.path.split(base_pathA)[1])
            rootA.setIcon(0, self.qicon)
            t1 = threading.Thread(target=self.addChild,args=(rootA, base_pathA, base_pathB))
            t1.start()
            t1.join()
            self.treeA.addTopLevelItem(rootA)
            self.treeA.expandAll()
        if base_pathB:
            rootB = QTreeWidgetItem(self.treeB)
            rootB.setText(0, os.path.split(base_pathB)[1])
            rootB.setIcon(0, self.qicon)
            t2 = threading.Thread(target=self.addChild,args=(rootB,base_pathB,base_pathA))
            t2.start()
            t2.join()
            self.treeB.addTopLevelItem(rootB)
            self.treeB.expandAll()
        # 设置qss样式
        qss_file = QFile(':/img/style1.qss')
        qss_file.open(QFile.ReadOnly)
        qss = str(qss_file.readAll(), encoding='utf-8')
        qss_file.close()
        self.treeA.setStyleSheet(qss)
        self.treeB.setStyleSheet(qss)

    def addChild(self,root_obj,path1,path2):
        # 迭代方式，用到的时候才创建，前一次循环的创建对象保存在列表中，供下一次循环创建使用
        list_root_last = [path1]
        list_obj_root_last = [root_obj]
        for root, dirs, files in os.walk(path1, topdown=False):
            list_obj_root_cur = []
            list_root_cur = []
            parent_root = root
            while True:
                # 得到从根路径到当前路径之间所有的目录路径
                if not parent_root == path1:
                    list_root_cur.append(parent_root)
                    parent_root = os.path.split(parent_root)[0]
                else:
                    list_root_cur.append(parent_root)
                    break
            list_root_cur.reverse()
            obj = root_obj
            for one in list_root_cur:
                if one in list_root_last:
                    idx = list_root_last.index(one)
                    obj = list_obj_root_last[idx]
                else:
                    # 不存在则创建
                    obj = QTreeWidgetItem(obj)
                    obj.setText(0, os.path.split(one)[1])
                    obj.setIcon(0, self.qicon)
                    newpath = one.replace(path1, path2)
                    if not os.path.exists(newpath):
                        if path2:
                            obj.setForeground(0, QBrush(Qt.red))
                list_obj_root_cur.append(obj)
            list_obj_root_last = list_obj_root_cur
            list_root_last = list_root_cur
            # print('list_obj_root_last', list_obj_root_last)
            # print('list_root_last', list_root_last)
            for file in files:
                file_obj = QTreeWidgetItem(obj)
                file_obj.setText(0, file)
                file_path = os.path.join(root, file)
                newpath = file_path.replace(path1, path2)
                if not os.path.exists(newpath):
                    if path2:
                        file_obj.setForeground(0, QBrush(Qt.red))

    # 给treewidget设置右键点击事件
    def createContextMenu(self,tree_obj,line_obj,contextMenu):
        tree_obj.setContextMenuPolicy(Qt.CustomContextMenu)
        self.actionA = contextMenu.addAction(u'|  修改')
        self.actionB = contextMenu.addAction(u'|  删除')
        # 显示菜单
        tree_obj.customContextMenuRequested.connect(lambda : self.showContextMenu(tree_obj,contextMenu))
        # 绑定操作
        self.actionA.triggered.connect(lambda: self.edit(tree_obj,line_obj))
        self.actionB.triggered.connect(lambda: self.remove(tree_obj,line_obj))

    def showContextMenu(self,tree_obj,contextMenu):
        # 如果有选中项，则显示右键菜单
        items = tree_obj.selectedIndexes()
        if items:
            contextMenu.show()
            # 在鼠标位置显示
            contextMenu.exec_(QCursor.pos())

    def showImage(self,tree_item,line_objA,line_objB):
        # 清除之前显示的图片
        self.labelA.clear()
        self.labelB.clear()
        if not tree_item:
            return
        urlA = self.getItemPath(tree_item, line_objA.text())
        urlB = self.getItemPath(tree_item, line_objB.text())
        flag = False
        if not os.path.isdir(urlA) and os.path.exists(urlA):
            try:
                im = Image.open(urlA)
                img = QImage(urlA)
                pixA = QPixmap.fromImage(img.scaled(self.imgAdapt(self.labelA,im)))
                self.labelA.setPixmap(pixA)
                flag = True
            except OSError:
                pass
        if not os.path.isdir(urlB) and os.path.exists(urlB):
            try:
                im = Image.open(urlB)
                img = QImage(urlB)
                pixB = QPixmap.fromImage(img.scaled(self.imgAdapt(self.labelB,im)))
                self.labelB.setPixmap(pixB)
                flag = True
            except OSError:
                pass
        if flag:
            self.addTab(self.tab2, "图片查看")
            self.setCurrentWidget(self.tab2)
        self.line_pathA.setText(urlA)
        self.line_pathB.setText(urlB)
        if not line_objA.text():
            self.line_pathA.setText('')
        if not line_objB.text():
            self.line_pathB.setText('')
        # 将双击打开图片时的item设为初始item
        self.next_item = tree_item

    # 调整初始显示的图片，以适应label大小
    def imgAdapt(self,label_obj,im):
        width = label_obj.size().width()
        height = label_obj.size().height()
        if im.size[1]*width/im.size[0]< height:
            return QSize(width, im.size[1]*width/im.size[0])
        return QSize(im.size[0]*height/im.size[1], height)

    # qtreewidget迭代器，用于遍历qtreewidget
    def tree_items(self,tree_obj):
        it = QTreeWidgetItemIterator(tree_obj)
        while it.value():
            yield it.value()
            it += 1

    def hasNextItem(self,tree_item):
        tree_list = []
        if self.treeA.currentItem():
            tree_obj = self.treeA
        elif self.treeB.currentItem():
            tree_obj = self.treeB
        else:
            return
        # 遍历treewidget
        for index, item in enumerate(self.tree_items(tree_obj)):
            if item.text(0).lower().endswith('.jpg') or item.text(0).lower().endswith('.png'):
                tree_list.append(item)
        if not tree_list:
            self.setCurrentWidget(self.tab1)
            return
        try:
            next_idx = tree_list.index(tree_item) + 1
        except ValueError:
            self.setCurrentWidget(self.tab1)
            return
        if next_idx > len(tree_list) - 1:
            self.next_item = tree_item
            return
        self.next_item = tree_list[next_idx]

    def hasBeforeItem(self,tree_item):
        tree_list = []
        if self.treeA.currentItem():
            tree_obj = self.treeA
        elif self.treeB.currentItem():
            tree_obj = self.treeB
        else:
            return
        # 遍历treewidget
        for index, item in enumerate(self.tree_items(tree_obj)):
            if item.text(0).lower().endswith('.jpg') or item.text(0).lower().endswith('.png'):
                tree_list.append(item)
        if not tree_list:
            self.setCurrentWidget(self.tab1)
            return
        try:
            before_idx = tree_list.index(tree_item) - 1
        except ValueError:
            self.setCurrentWidget(self.tab1)
            return
        if before_idx < 0:
            self.next_item = tree_item
            return
        self.next_item = tree_list[before_idx]

    def edit(self,tree_obj,line_obj):
        file_name = tree_obj.currentItem().text(0)
        self.uidialog = UiDialog()
        self.uidialog.btn_confirm.clicked.connect(lambda : self.renameFile(tree_obj,line_obj))
        self.uidialog.btn_cancel.clicked.connect(self.cancel)
        self.uidialog.filename_edit.setText(file_name)
        self.uidialog.filename_edit.setFocus()
        self.uidialog.show()

    def renameFile(self,tree_obj,line_obj):
        src = self.getItemPath(tree_obj.currentItem(),line_obj.text())
        dst = '/'.join((os.path.dirname(src),self.uidialog.filename_edit.text()))
        if src == '/'.join((line_obj.text(), '')):
            self.addInfo(u'根目录不可修改！')
            self.uidialog.close()
            return
        try:
            os.rename(src,dst)
        except FileExistsError:
            self.addInfo(u'修改失败，名称重复！')
            self.uidialog.close()
            return
        self.addInfo('modify', tree_obj.currentItem(), line_obj)
        self.uidialog.close()
        # 重新加载
        self.loadDir()

    def getItemPath(self,parent,root):
        lib = []
        while parent:
            lib.append(parent.text(0))
            parent = parent.parent()
        lib.reverse()
        part = '/'.join(lib[1:])
        return '/'.join((root, part))

    def cancel(self):
        self.uidialog.close()

    def remove(self,tree_obj,line_obj):
        path = self.getItemPath(tree_obj.currentItem(), line_obj.text())
        if os.path.isdir(path):
            if path == '/'.join((line_obj.text(), '')):
                self.addInfo(u'根目录不可删除！')
                return
            else:
                shutil.rmtree(path)
        else:
            os.remove(path)
        self.addInfo('delete', tree_obj.currentItem(), line_obj)
        # 重新加载
        self.loadDir()


if __name__=="__main__":
    app=QApplication(sys.argv)
    win=WindowClass()
    win.showMaximized()
    sys.exit(app.exec_())