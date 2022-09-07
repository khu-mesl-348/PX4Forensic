from src.Mission.tools import cmd_cd, cmd_ls, cmd_cd_back


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

    # mav_serialport에 연결된 드론의 쉘 커맨드를 이용해 파일 목록을 불러오는 함수
    # @input: root 노드
    # @output: 드론의 파일/폴더를 노드로 하는 트리
    def dfs(self, root, blacklist=[]):
        # 오류, 혹은 사용되지 않는 디렉토리 및 파일

        datalist =[]
        self.stack.append(root)
        self.root.data = root
        cur = self.root
        count = 0
        cmd_cd("/", self.mav_serialport)
        while len(self.stack) != 0:
            item = self.stack.pop()

            # print(item)

            if item == "..":
                if len(self.stack) == 1:
                    break
                cmd_cd_back(self.mav_serialport)
                if cur.data != '/':
                    cur = cur.parent
                continue

            elif "/" in item and item not in blacklist:
                cmd_cd(item, self.mav_serialport)
                self.stack.append("..")
                datalist = cmd_ls(self.mav_serialport)
                for next in cur.child:
                    if next.data == item:
                        cur = next
                        break
            elif "/" not in item and item not in blacklist:
                count += 1

            if len(datalist) != 0:
                for idx, item in enumerate(datalist):
                    if idx < 2:
                        continue
                    if item not in blacklist:
                        self.stack.append(item)
                        leaf = Node(item)
                        cur.append_child(leaf)

            datalist.clear()
        return count

    def get_root(self):
        return self.root


