from PX4Forensic.src.tools import cmd_cd, cmd_ls

# 트리 노드 생성
class Node:
    def __init__(self, data):
        self.data = data
        self.child = []
        self.parent = None

    def append_child(self, new_node):
        new_node.parent = self
        self.child.append(new_node)


class Tree:
    def __init__(self, mav_serialport):
        self.stack = []
        self.files = []
        self.mav_serialport = mav_serialport
        self.root = Node("/")

    # ls
    def dfs(self, root):
        self.stack.append(root)
        self.root.data = root
        cur = self.root
        while len(self.stack) != 0:
            print(self.stack)
            print("cur: ", cur.data)
            item = self.stack.pop()
            print("cur: ", cur.data)

            # print(item)

            if item == "..":
                if (len(self.stack) == 1):
                    break
                cmd_cd_back(self.mav_serialport)
                if cur.data != '/':
                    cur = cur.parent
                continue

            elif "/" in item and item not in blacklist:
                cmd_cd(item, self.mav_serialport)
                self.stack.append("..")
                cmd_ls(self.mav_serialport)
                for next in cur.child:
                    print("next: ", next.data, "itm: ", item)
                    if next.data == item:
                        cur = next
                        break

            if (len(datalist) != 0):
                for idx, item in enumerate(datalist):
                    if idx < 2:
                        continue
                    self.stack.append(item)

                    leaf = Node(item)
                    cur.append_child(leaf)

            datalist.clear()

    # 구성된 트리를 dfs 탐색하는 함수
    def search(self):
        st = []
        st.append(self.root)

        while len(st) > 0:
            item = st.pop()
            for sub in item.child:
                filename = ''
                cur = sub
                if cur.data.find('/') == -1:
                    while cur.parent != None:
                        filename = cur.data.replace(" ", "") + filename
                        cur = cur.parent

                    # root 경로 추가
                    filename = '/' + filename

                    # 여기서 각 파일의 경로+파일명이 생성됩니다
                    print(filename)

                st.append(sub)
