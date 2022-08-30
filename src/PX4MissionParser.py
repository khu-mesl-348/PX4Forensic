import struct
import os
import sys
from model import *


global g_per_item_size
global g_per_item_max_index
global g_key_offsets


def init(_env = ""):
    global g_per_item_max_index
    global g_per_item_size
    global g_key_offsets
    
    # 각 영역별 크기
    g_per_item_size = [dm_size.SAFE_POINTS_SIZE.value + DM_SECTOR_HDR_SIZE, dm_size.FENCE_POINTS_SIZE.value + DM_SECTOR_HDR_SIZE, dm_size.WAYPOINTS_OFFBOARD_SIZE.value + DM_SECTOR_HDR_SIZE, dm_size.WAYPOINTS_OFFBOARD_SIZE.value + DM_SECTOR_HDR_SIZE, dm_size.MISSION_STATE_SIZE.value + DM_SECTOR_HDR_SIZE, dm_size.KEY_COMPAT_SIZE.value + DM_SECTOR_HDR_SIZE]

    # 각 영역별 최대 인덱스
    if _env == "" or _env == "RAM_BASED_MISSIONS":         
        g_per_item_max_index = [dm_item_s.DM_KEY_SAFE_POINTS_MAX.value, dm_item_s.DM_KEY_FENCE_POINTS_MAX.value, dm_item_s.DM_KEY_WAYPOINTS_OFFBOARD_0_MAX.value, dm_item_s.DM_KEY_WAYPOINTS_OFFBOARD_1_MAX.value, dm_item_s.DM_KEY_MISSION_STATE_MAX.value,  dm_item_s.DM_KEY_COMPAT_MAX.value]
    elif _env == "MEMORY_CONSTRAINED_SYSTEM":
        g_per_item_max_index = [dm_item_s_constrained.DM_KEY_SAFE_POINTS_MAX.value, dm_item_s_constrained.DM_KEY_FENCE_POINTS_MAX.value, dm_item_s_constrained.DM_KEY_WAYPOINTS_OFFBOARD_0_MAX.value, dm_item_s_constrained.DM_KEY_WAYPOINTS_OFFBOARD_1_MAX.value, dm_item_s_constrained.DM_KEY_MISSION_STATE_MAX.value,  dm_item_s_constrained.DM_KEY_COMPAT_MAX.value]
    elif _env == "_PX4_POSIX":
        g_per_item_max_index = [dm_item_s_px4_posix.DM_KEY_SAFE_POINTS_MAX.value, dm_item_s_px4_posix.DM_KEY_FENCE_POINTS_MAX.value, dm_item_s_px4_posix.DM_KEY_WAYPOINTS_OFFBOARD_0_MAX.value, dm_item_s_px4_posix.DM_KEY_WAYPOINTS_OFFBOARD_1_MAX.value, dm_item_s_px4_posix.DM_KEY_MISSION_STATE_MAX.value,  dm_item_s_px4_posix.DM_KEY_COMPAT_MAX.value]
    
    g_key_offsets = [0 for i in range(dm_item_t.DM_KEY_NUM_KEYS.value)]
    
    g_key_offsets[0] = 0
    
    # 각 영역별 오프셋 계산
    for i in range (dm_item_t.DM_KEY_NUM_KEYS.value - 1):
        g_key_offsets[i + 1] = g_key_offsets[i] + g_per_item_max_index[i] * g_per_item_size[i]

# 데이터의 오프셋을 구하는 함수
# input:    dm_item_t item: 아이템 종류
#           unsigned index: 아이템 인덱스
# output:   index of item(unsigned)       
        
def calculate_offset(item, index):
    global g_per_item_max_index
    global g_key_offsets
    global g_per_item_size
    
    if item >= dm_item_t.DM_KEY_NUM_KEYS.value:
        return -1
    if index >= g_per_item_max_index[item]:
        return -1
    return g_key_offsets[item] + (index * g_per_item_size[item]);



# dataman 내용을 읽는 함수
# @input:   int fd: file descripter
#           dm_item_t item: 아이템 종류
#           unsigned index: 아이템 인덱스
#           void* buf:      아이템 내용을 저장할 버퍼 위치
#           size_t count:   불러올 길이
# output:   읽어들인 데이터의 길이

def dmread(fd, item, index, buf, count):
    global g_per_item_size
    if item >= dm_item_t.DM_KEY_NUM_KEYS.value:
        return -1
    
    buffer = [0 for i in range(g_per_item_size[item])]
    offset = calculate_offset(item, index);
    #print(f"index: {index}, offset: {hex(offset)}")
    
    if offset < 0:
        return -1
    if count > (g_per_item_size[item] - DM_SECTOR_HDR_SIZE):
        return -1
    
    len = -1
    read_success = 0
    for i in range(2):
        ret_seek = os.lseek(fd, offset, os.SEEK_SET)
        if ret_seek < 0:
            print("file read lseek failed")
            continue
        
        #print("offset: %lx, ret_seek: %x, count: %lx\n",offset,ret_seek,count + DM_SECTOR_HDR_SIZE, index)
        
        if ret_seek != offset:
            print("file read lseek failed, incorrect offset {} vs {}", ret_seek, offset)
            continue
        buffer = os.read(fd, count + DM_SECTOR_HDR_SIZE)

        #print(buffer, count+DM_SECTOR_HDR_SIZE)
        #print(buffer)
        #print("read result: len: %x, count: %x, size: %x\n", len, count+DM_SECTOR_HDR_SIZE,buffer[0]);
  
        if buffer[0] >= 0:
            read_success = 1
            break
        if not read_success:
            return -1
    
    if len == 0:
        buffer[0] = 0
    
    if buffer[0] > 0:
        if buffer[0] > count:
            return -1

    if type(buf) == mission_stats_entry_s:
        buf.num_items = buffer[4] + buffer[5]*256
        buf.update_counter = buffer[6] + buffer[7] * 256

    elif type(buf) == mission_safe_point_s:
        buf.lat = struct.unpack('d', buffer[4:12])[0]
        buf.lon = struct.unpack('d', buffer[12:20])[0]
        buf.alt = struct.unpack('f', buffer[20:24])[0]
        buf.frame = buffer[24]

    elif type(buf) == mission_fence_point_s:
        buf.lat = struct.unpack('d', buffer[4:12])[0]
        buf.lon = struct.unpack('d', buffer[12:20])[0]
        buf.alt = struct.unpack('f', buffer[20:24])[0]
        buf.vertex_count = b_to_i(buffer[24:26], 2)
        buf.circle_radius = struct.unpack('f', buffer[24:28])[0]
        buf.nav_cmd = b_to_i(buffer[28:30], 2)
        buf.frame = buffer[30]

    elif type(buf) == mission_item_s:
        #print(offset, buffer, buffer[0])
        buf.lat = struct.unpack('d', buffer[4:12])[0]
        buf.lon = struct.unpack('d', buffer[12:20])[0]
        buf.time_inside = struct.unpack('f', buffer[20:24])[0]
        buf.circle_radius = struct.unpack('f', buffer[20:24])[0]
        buf.acceptance_radius = struct.unpack('f', buffer[24:28])[0]
        buf.loiter_radius = struct.unpack('f', buffer[28:32])[0]
        buf.yaw = struct.unpack('f', buffer[32:36])[0]
        buf.___lat_float = struct.unpack('f', buffer[36:40])[0]
        buf.___lon_float = struct.unpack('f', buffer[40:44])[0]
        buf.altitude = struct.unpack('f', buffer[44:48])[0]

        for i in range(7):
            buf.params[i] = struct.unpack('f', buffer[20+i*4: 24+i*4])[0]

        buf.nav_cmd = struct.unpack('H', buffer[48:50])[0]
        buf.do_jump_mission_index = struct.unpack('h', buffer[50:52])[0]
        buf.do_jump_repeat_count = struct.unpack('H', buffer[52:54])[0]

        buf.do_jump_current_count  = struct.unpack('H', buffer[54:56])[0]
        buf.vertex_count = struct.unpack('H', buffer[54:56])[0]
        buf.land_precision = struct.unpack('H', buffer[54:56])[0]

        buf.frame = (buffer[56] & 0b00001111)
        buf.origin = (buffer[56] & 0b01110000) >> 4
        buf.loiter_exit_xtrack = (buffer[56] & 0b10000000)
        buf.force_heading = (buffer[57] & 0b00000001)
        buf.altitude_is_relative = (buffer[57] & 0b00000010) >> 1
        buf.autocontinue = (buffer[57] & 0b00000100) >> 2
        buf.vtol_back_transition =(buffer[57] & 0b00001000) >> 3

    elif type(buf) == mission_s:

        buf.timestamp = struct.unpack('Q', buffer[4:12])[0]
        buf.current_seq = struct.unpack('i', buffer[12:16])[0]
        buf.count = struct.unpack('H', buffer[16:18])[0]
        buf.dataman_id = buffer[18]

    elif type(buf) == dataman_compat_s:
        buf.key = struct.unpack('Q', buffer[4:12])[0]
    else:
        return -1
    
    return buffer[0]


def get_safe_points(fd):
    res = []
    stats_safe = mission_stats_entry_s()
# read safe points
    ret = dmread(fd, dm_item_t.DM_KEY_SAFE_POINTS.value, 0, stats_safe, dm_size.ENTRY_SIZE.value)
    res.append(stats_safe)

    num_safe_points = 0
    if ret == dm_size.ENTRY_SIZE.value:
        num_safe_points = stats_safe.num_items;
    
    print("mission_safe_point\n------------------\n");
    print(f"number of safe points: {num_safe_points}, update_counter: {stats_safe.update_counter}\n");
    for current_seq in range(1, num_safe_points+1):
        mission_safe_point = mission_safe_point_s(0,0,0,0)
        ret = dmread(fd, dm_item_t.DM_KEY_SAFE_POINTS.value, current_seq, mission_safe_point, dm_size.SAFE_POINTS_SIZE.value)
        res.append(mission_safe_point)

        if ret != dm_size.SAFE_POINTS_SIZE.value:
            print("dm_read failed\n")
            continue

		#printf("ret: %d, size: %ld\n",ret ,sizeof(struct mission_safe_point_s));
        print(f"{current_seq} th point: lat: {mission_safe_point.lat}, lon: {mission_safe_point.lon}, alt: {mission_safe_point.alt}, frame: {mission_safe_point.frame}")

    return res


def get_fence_points(fd):
    res = []

    stats_fence = mission_stats_entry_s()
    ret = dmread(fd, dm_item_t.DM_KEY_FENCE_POINTS.value, 0, stats_fence, dm_size.ENTRY_SIZE.value)
    res.append(stats_fence)

    num_fence_items = 0
    current_seq = 1

    if ret == dm_size.ENTRY_SIZE.value:
        num_fence_items = stats_fence.num_items

    print("mission_fence_point\n------------------\n")
    print(f"number of fence points: {num_fence_items}, update_counter: {stats_fence.update_counter}")
    vertex_count_temp = 0

    while current_seq <= num_fence_items:
        mission_fence_point = mission_fence_point_s(0,0,0,0,0,0,0)
        is_circle_area = 0

        ret = dmread(fd, dm_item_t.DM_KEY_FENCE_POINTS.value, current_seq, mission_fence_point, dm_size.FENCE_POINTS_SIZE.value)
        res.append(mission_fence_point)

        if ret != dm_size.FENCE_POINTS_SIZE.value:
            print("dm_read failed")
            break

        if mission_fence_point.nav_cmd == NAV_CMD.FENCE_POLYGON_VERTEX_INCLUSION.value and vertex_count_temp == 0:
            print(f"number of vertex: {mission_fence_point.vertex_count}")
            vertex_count_temp = mission_fence_point.vertex_count

        print(f"{current_seq} th point: lat: {mission_fence_point.lat}, lon: {mission_fence_point.lon}, alt: {mission_fence_point.alt}, frame: {mission_fence_point.frame}")

        if mission_fence_point.nav_cmd == NAV_CMD.FENCE_RETURN_POINT.value:
            current_seq += 1
        elif mission_fence_point.nav_cmd == NAV_CMD.FENCE_CIRCLE_INCLUSION.value or mission_fence_point.nav_cmd == NAV_CMD.FENCE_CIRCLE_EXCLUSION.value:
            is_circle_area = 1
            print(f"radius: {mission_fence_point.circle_radius}, nav_cmd: {mission_fence_point.nav_cmd}, frame: {mission_fence_point.frame}")

            if is_circle_area == 0 and mission_fence_point.vertex_count == 0:
                current_seq += 1
                print("Polygon with 0 vertices. Skipping")
            else:
                if is_circle_area != 0:
                    current_seq += 1

                else:
                    current_seq += 1
                    vertex_count_temp -= 1;
                    print(
                        f"vertex: {mission_fence_point.vertex_count}, nav_cmd: {mission_fence_point.nav_cmd}, frame: {mission_fence_point.frame}");
                    if vertex_count_temp == 0:
                        print("\n");

        elif mission_fence_point.nav_cmd == NAV_CMD.FENCE_POLYGON_VERTEX_EXCLUSION.value or mission_fence_point.nav_cmd == NAV_CMD.FENCE_POLYGON_VERTEX_INCLUSION.value:
            if is_circle_area == 0 and mission_fence_point.vertex_count == 0:
                current_seq += 1
                print("Polygon with 0 vertices. Skipping")
            else:
                if is_circle_area != 0:
                    current_seq += 1

                else:
                    current_seq += 1
                    vertex_count_temp -= 1;
                    print(f"vertex: {mission_fence_point.vertex_count}, nav_cmd: {mission_fence_point.nav_cmd}, frame: {mission_fence_point.frame}");
                    if vertex_count_temp == 0:
                        print("\n");

        else:
            print(f"unhandled Fence command: {mission_fence_point.nav_cmd}")
            current_seq += 1

    return res


def get_mission_item(fd, dataman_id):

    res = []

    missionitem = mission_item_s(0, 0, 0, 0, 0, 0, 0, 0, [0,0,0,0,0,0,0], 0,0,0,0,0,0,0,0,0,0,0)

    if dataman_id == 2:
        print("\nkey_waypoints_0\n------------------\n")
        dmsize = dm_item_s.DM_KEY_WAYPOINTS_OFFBOARD_0_MAX.value
    elif dataman_id == 3:
        print("\nkey_waypoints_1\n------------------\n")
        dmsize = dm_item_s.DM_KEY_WAYPOINTS_OFFBOARD_1_MAX.value
    else:
        print("invaild datamam id")
        return [-1]

    for i in range(dmsize):
        ret = dmread(fd, dataman_id, i, missionitem, dm_size.WAYPOINTS_OFFBOARD_SIZE.value)
        if ret != dm_size.WAYPOINTS_OFFBOARD_SIZE.value:
            #print("dataman read failure")
            continue
        res.append(missionitem)
        print(f"{i} th item: ")
        print(f"nav_cmd: {missionitem.nav_cmd}, lat: {missionitem.lat}, lon: {missionitem.lon}, alt: {missionitem.altitude}, frame: {missionitem.frame}")
        print(f"force heading: {missionitem.force_heading}, relative altitude: {missionitem.altitude_is_relative}, autocontinue: {missionitem.autocontinue}, vtol back transition: {missionitem.vtol_back_transition}")

    return res


def get_mission(fd):
    mission = mission_s(0,0,0,0)
    ret = dmread(fd, dm_item_t.DM_KEY_MISSION_STATE.value, 0, mission, dm_size.MISSION_STATE_SIZE.value)
    print("\nkey_mission_state\n------------------");

    if ret == dm_size.MISSION_STATE_SIZE.value:
        if mission.timestamp != 0 and mission.dataman_id == dm_item_t.DM_KEY_WAYPOINTS_OFFBOARD_0.value or mission.dataman_id == dm_item_t.DM_KEY_WAYPOINTS_OFFBOARD_1.value:
            if mission.count > 0:
                print(f"timestamp: {mission.timestamp} , seq: {mission.current_seq} count: {mission.count} dataman_id: {mission.dataman_id}")
        else:
            print("reading mission state failed\n")

    return mission

def get_key_compat(fd):
    print("\nkey_compat\n------------------");
    key_compat = dataman_compat_s(0)
    ret = dmread(fd, dm_item_t.DM_KEY_COMPAT.value, 0, key_compat, dm_size.KEY_COMPAT_SIZE.value)
    if ret == dm_size.KEY_COMPAT_SIZE.value:
        print(f"key: {key_compat.key}\n")

    return key_compat

def main():
    if not len(sys.argv) == 2 or sys.argv[1] == "help":	
        print("[usage]: ./parser <file name> \n")
        return 1    
    print(sys.argv[1])
    fd = os.open(sys.argv[1], os.O_BINARY)
    if fd == -1:
        print("invaild file\n")
        return 1
    
    init()
    
    get_safe_points(fd)
    get_fence_points(fd)
    get_mission_item(fd, dm_item_t.DM_KEY_WAYPOINTS_OFFBOARD_0.value)
    get_mission_item(fd, dm_item_t.DM_KEY_WAYPOINTS_OFFBOARD_1.value)
    get_mission(fd)
    get_key_compat(fd)
    
if __name__ == '__main__':
    main()