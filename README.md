# PX4 Forensic project
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-5-orange.svg?style=flat-square)](#contributors)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

# Introduction 📖
> ###PX4 Autopilot 내부 데이터를 분석하고 무결성 검증을 제공하는 응용 프로그램입니다.
* 무결성 검증 기능은 khu-mesl-348/PX4-Autopilot 펌웨어와 호환됩니다.
* 일부 기능은 PX4와 USB Serial 연결이 필요합니다.
# Getting Started 💡
## 1. Download resource
```commandline
cd C:\Users\{username}\Desktop
git clone https://github.com/khu-mesl-348/PX4Forensic.git
```

## 2. install packages

![python3.9](https://img.shields.io/badge/python-3.9-blue) 
![altgraph](https://img.shields.io/badge/altgraph-0.17.3-random)
![bson](https://img.shields.io/badge/bson-0.5.10-random)
![contourpy](https://img.shields.io/badge/contourpy-1.0.5-random)
![crccheck](https://img.shields.io/badge/crccheck-1.2.0-random)
![cycler](https://img.shields.io/badge/cycler-0.11.0-random)
![fonttools](https://img.shields.io/badge/fonttools-4.37.2-random)
![future](https://img.shields.io/badge/future-0.18.2-random)
![haversine](https://img.shields.io/badge/haversine-2.7.0-random)
![iso8601](https://img.shields.io/badge/iso8601-1.0.2-random)
![kiwisolver](https://img.shields.io/badge/kiwisolver-1.4.4-random)
![lxml](https://img.shields.io/badge/lxml-4.9.1-random)
![matplotlib](https://img.shields.io/badge/matplotlib-3.6.0-random)
![numpy](https://img.shields.io/badge/numpy-1.23.3-random)
![packaging](https://img.shields.io/badge/packaging-21.3-random)
![pandas](https://img.shields.io/badge/pandas-1.4.4-random)
![pefile](https://img.shields.io/badge/pefile-2022.5.30-random)
![Pillow](https://img.shields.io/badge/Pillow-9.2.0-random)
![pymavlink](https://img.shields.io/badge/pymavlink-2.4.31-random)
![pyparsing](https://img.shields.io/badge/pyparsing-3.0.9-random)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15.7-random)
![pyserial](https://img.shields.io/badge/pyserial-3.5-random)
![pytz](https://img.shields.io/badge/pytz-2022.2.1-random)
![PyYAML](https://img.shields.io/badge/PyYAML-6.0-random)
![six](https://img.shields.io/badge/six-1.16.0-random)
![pyulog](https://img.shields.io/badge/pyulog-1.0.0-random)
```
pip install -r requirements.txt
```

* Windows 환경에서 사용 시
```
pip install windows-curses
```


## 3. Execution
### 모듈 적용
1. `/module/integrity_tools` 를 PX4 소스의  `/src/modules` 하위에 이동
2. `/module/default.px4board`를 `/board/px4/fmu-v5` 하위에 이동

### 분석 도구 실행
```
python main.py
```

# How to Use 💻
## 1. 사용자 인증
* PX4에 로그인이 되어 있지 않을 시 ID, 비밀번호 입력란과 로그인 버튼이 활성화됩니다.
* PX4에 로그인이 되어 있을 시 입력란이 비활성화되며 로그아웃 버튼이 활성화됩니다.

## 2. 비행 데이터 분석
아래 세 가지 지점들 중 Radiopoint로 선택한 지점들의 정보를 나타냅니다.
* Safe points
  * 위치
* Fence points
  * 위치, 모양, 꼭짓점 개수 혹은 반경
* Waypoints
  * 위치, 임무 종류 등


## 3. 로그 데이터 분석
로그 데이터에 대한 정보를 보여줍니다.
* File info
* Message
* Parameters

## 4. 설정 데이터 분석
파라미터에 대한 정보를 보여줍니다.
* Value
* Range
* Description

# Contributors ✨

<div align="center">
<a href="https://mesl.khu.ac.kr"><img src="./logo.png" width="20%;" alt=""/></a>
<h2 href="https://mesl.khu.ac.kr">MESL</h2>


<br>
Thanks goes to these wonderful people :

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://github.com/sju0924"><img src="https://avatars.githubusercontent.com/u/39671049?v=4" width="100px;" alt=""/><br /><sub><b>serendipity</b></sub></a></td>
    <td align="center"><a href="https://github.com/Kimbongsik"><img src="https://avatars.githubusercontent.com/u/63995044?v=4" width="100px;" alt=""/><br /><sub><b>Yoo youngbeen</b></sub></a></td>
    <td align="center"><a href="https://github.com/bpsswu"><img src="https://avatars.githubusercontent.com/u/101001675?v=4" width="100px;" alt=""/><br /><sub><b>bpsswu</b></sub></a></td>
    <td align="center"><a href="https://github.com/sirkang1208"><img src="https://avatars.githubusercontent.com/u/104350527?v=4" width="100px;" alt=""/><br /><sub><b>sirkang1208</b></sub></a></td>
    <td align="center"><a href="https://github.com/beerabbit"><img src="https://avatars.githubusercontent.com/u/57741072?v=4" width="100px;" alt=""/><br /><sub><b>icetream</b></sub></a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->



This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
</div>

---
