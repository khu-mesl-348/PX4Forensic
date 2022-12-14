# PX4 Forensic project
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-5-orange.svg?style=flat-square)](#contributors)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

# Introduction π
> ###PX4 Autopilot λ΄λΆ λ°μ΄ν°λ₯Ό λΆμνκ³  λ¬΄κ²°μ± κ²μ¦μ μ κ³΅νλ μμ© νλ‘κ·Έλ¨μλλ€.
* λ¬΄κ²°μ± κ²μ¦ κΈ°λ₯μ khu-mesl-348/PX4-Autopilot νμ¨μ΄μ νΈνλ©λλ€.
* μΌλΆ κΈ°λ₯μ PX4μ USB Serial μ°κ²°μ΄ νμν©λλ€.
# Getting Started π‘
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

* Windows νκ²½μμ μ¬μ© μ
```
pip install windows-curses
```

* Linux νκ²½μμ μ¬μ© μ
> /ui/PX4Forensic.py νμΌμμ Serial={PX4κ° μ°κ²°λ μλ¦¬μΌ ν¬νΈλͺ} μΌλ‘ μ€μ ν΄μ€λ€. 
> ex) Serial = '/dev/ttyACM0'

## 3. Execution
### λͺ¨λ μ μ©
1. `/module/integrity_tools` λ₯Ό PX4 μμ€μ  `/src/modules` νμμ μ΄λ
2. `/module/default.px4board`λ₯Ό `/board/px4/fmu-v5` νμμ μ΄λ
3. HMAC μμ±νκ³ μ νλ μ½λ μμΉμ API μ μ©

### λΆμ λκ΅¬ μ€ν
```
python main.py
```

# How to Use π»
## 1. μ¬μ©μ μΈμ¦
* PX4μ λ‘κ·ΈμΈμ΄ λμ΄ μμ§ μμ μ ID, λΉλ°λ²νΈ μλ ₯λκ³Ό λ‘κ·ΈμΈ λ²νΌμ΄ νμ±νλ©λλ€.
* PX4μ λ‘κ·ΈμΈμ΄ λμ΄ μμ μ μλ ₯λμ΄ λΉνμ±νλλ©° λ‘κ·Έμμ λ²νΌμ΄ νμ±νλ©λλ€.

## 2. λΉν λ°μ΄ν° λΆμ
μλ μΈ κ°μ§ μ§μ λ€ μ€ Radiopointλ‘ μ νν μ§μ λ€μ μ λ³΄λ₯Ό λνλλλ€.
* Safe points
  * μμΉ
* Fence points
  * μμΉ, λͺ¨μ, κΌ­μ§μ  κ°μ νΉμ λ°κ²½
* Waypoints
  * μμΉ, μλ¬΄ μ’λ₯ λ±


## 3. λ‘κ·Έ λ°μ΄ν° λΆμ
λ‘κ·Έ λ°μ΄ν°μ λν μ λ³΄λ₯Ό λ³΄μ¬μ€λλ€.
* ULog files
* File info
* Message
* Parameters

## 4. μ€μ  λ°μ΄ν° λΆμ
νλΌλ―Έν°μ λν μ λ³΄λ₯Ό λ³΄μ¬μ€λλ€.
* Parameters
* Value
* Range
* Description

# Contributors β¨

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
