from enum import Enum
DM_SECTOR_HDR_SIZE = 4
UINT16_MAX = 65535

def b_to_i(b, l):
	res = 0
	for i in range(l):
		res += b[i]*pow(256, i)

	return res
class dm_item_t(Enum):
	DM_KEY_SAFE_POINTS = 0
	DM_KEY_FENCE_POINTS = 1		
	DM_KEY_WAYPOINTS_OFFBOARD_0 = 2
	DM_KEY_WAYPOINTS_OFFBOARD_1 = 3
	DM_KEY_MISSION_STATE = 4
	DM_KEY_COMPAT = 5
	DM_KEY_NUM_KEYS	= 6

#if defined(MEMORY_CONSTRAINED_SYSTEM)
class dm_item_s_constrained(Enum):
	DM_KEY_SAFE_POINTS_MAX = 8
	DM_KEY_FENCE_POINTS_MAX = 16
	DM_KEY_WAYPOINTS_OFFBOARD_0_MAX = 50
	DM_KEY_WAYPOINTS_OFFBOARD_1_MAX = 50
	DM_KEY_MISSION_STATE_MAX = 1
	DM_KEY_COMPAT_MAX = 1
 
 #if defined(__PX4_POSIX)
class dm_item_s_px4_posix(Enum):
	DM_KEY_SAFE_POINTS_MAX = 8
	DM_KEY_FENCE_POINTS_MAX = 16
	DM_KEY_WAYPOINTS_OFFBOARD_0_MAX = UINT16_MAX-1
	DM_KEY_WAYPOINTS_OFFBOARD_1_MAX = UINT16_MAX-1
	DM_KEY_MISSION_STATE_MAX = 1
	DM_KEY_COMPAT_MAX = 1
 

class dm_item_s(Enum):
	DM_KEY_SAFE_POINTS_MAX = 8
	DM_KEY_FENCE_POINTS_MAX = 64
	DM_KEY_WAYPOINTS_OFFBOARD_0_MAX = 500
	DM_KEY_WAYPOINTS_OFFBOARD_1_MAX = 500
	DM_KEY_MISSION_STATE_MAX = 1
	DM_KEY_COMPAT_MAX = 1



class mission_safe_point_s: 
    def __init__(self, _lat, _lon, _alt, _frame):
        self.lat = _lat
        self.lon = _lon
        self.alt = _alt
        self.frame = _frame
        _padding0 = [0,0,0]


class mission_fence_point_s:
	def __init__(self, _lat, _lon, _alt, _vertex_count, _circle_radius, _nav_cmd, _frame):
		self.lat = _lat
		self.lon = _lon
		self.alt = _alt
		self.vertex_count = _vertex_count
		self.circle_radius = _circle_radius
		self.nav_cmd = _nav_cmd
		self.frame = _frame
		_padding = [0,0,0,0,0]

class mission_item_s:
    def __init__(self,_lat, _lon, _time_inside,  _circle_radius, _acceptance_radius, _loiter_radius, _yaw, _altitude, _params,_nav_cmd, _do_jump_mission_index, _do_jump_repeat_count, _union1, _frame, _origin, _loiter_exit_xtrack, _force_heading, _altitude_is_relative, _autocontinue, _vtol_back_transition):
        self.lat = _lat
        self.lon = _lon
        self.time_inside = _time_inside
        self.circle_radius = _circle_radius
        self.acceptance_radius  = _acceptance_radius
        self.loiter_radius = _loiter_radius
        self.yaw  = _yaw
        self.altitude = _altitude
        self.params = _params
        self.nav_cmd = _nav_cmd
        self.do_jump_mission_index = _do_jump_mission_index
        self.do_jump_repeat_count = _do_jump_repeat_count

        self.union = _union1
        self.frame = _frame
        self.origin = _origin
        self.loiter_exit_xtrack = _loiter_exit_xtrack
        self.force_heading = _force_heading 
        self.altitude_is_relative = _altitude_is_relative
        self.autocontinue = _autocontinue
        self.vtol_back_transition = _vtol_back_transition
        self._padding0 = [0,0,0,0]


class mission_s:
    def __init__(self, _timestamp, _current_seq, _count, _dataman_id):   
        self.timestamp = _timestamp
        self.current_seq = _current_seq;
        self.count = _count
        self.dataman_id =  _dataman_id;
 
 

class dataman_compat_s: 
    def __init__(self, _key):
        self.key = _key

class mission_stats_entry_s:
    def __init__(self, _num_items = -1, _update_counter = -1):
        self.num_items = _num_items
        self.update_counter = _update_counter

class dm_size(Enum):
    ENTRY_SIZE = 4
    SAFE_POINTS_SIZE = 24
    FENCE_POINTS_SIZE = 32
    WAYPOINTS_OFFBOARD_SIZE = 56
    MISSION_STATE_SIZE = 16
    KEY_COMPAT_SIZE = 8
    

class NAV_CMD(Enum):
	IDLE = 0
	WAYPOINT = 16
	LOITER_UNLIMITED = 17
	LOITER_TIME_LIMIT = 19
	RETURN_TO_LAUNCH = 20
	LAND = 21
	TAKEOFF = 22
	LOITER_TO_ALT = 31
	DO_FOLLOW_REPOSITION = 33
	VTOL_TAKEOFF = 84
	VTOL_LAND = 85
	DELAY = 93
	DO_JUMP = 177
	DO_CHANGE_SPEED = 178
	DO_SET_HOME = 179
	DO_SET_SERVO = 183
	DO_LAND_START = 189
	DO_SET_ROI_LOCATION = 195
	DO_SET_ROI_WPNEXT_OFFSET = 196
	DO_SET_ROI_NONE = 197
	DO_CONTROL_VIDEO = 200
	DO_SET_ROI = 201
	DO_DIGICAM_CONTROL = 203
	DO_MOUNT_CONFIGURE = 204
	DO_MOUNT_CONTROL = 205
	DO_SET_CAM_TRIGG_INTERVAL = 214
	DO_SET_CAM_TRIGG_DIST = 206
	OBLIQUE_SURVEY = 260
	SET_CAMERA_MODE = 530
	SET_CAMERA_ZOOM = 531
	SET_CAMERA_FOCUS = 532
	DO_GIMBAL_MANAGER_PITCHYAW = 1000
	DO_GIMBAL_MANAGER_CONFIGURE = 1001
	IMAGE_START_CAPTURE = 2000
	IMAGE_STOP_CAPTURE = 2001
	DO_TRIGGER_CONTROL = 2003
	VIDEO_START_CAPTURE = 2500
	VIDEO_STOP_CAPTURE = 2501
	DO_VTOL_TRANSITION = 3000
	FENCE_RETURN_POINT = 5000
	FENCE_POLYGON_VERTEX_INCLUSION = 5001
	FENCE_POLYGON_VERTEX_EXCLUSION = 5002
	FENCE_CIRCLE_INCLUSION = 5003
	FENCE_CIRCLE_EXCLUSION = 5004
	CONDITION_GATE = 4501
	INVALID = UINT16_MAX

