<div align="center">
  <img
    src="dns_monkey.ico"
    alt="DNS Monkey - A simple DNS changer for Windows"
  >
  <h1>DNS Monkey</h1>
</div>

If you change your Windows DNS regularly, you know how much of a pain in the neck it is.<br>
**DNS Monkey** is a simple DNS changer that sits in your systray, so you have easy access to it.<br>
You can download the latest version from [here](https://github.com/amis-shokoohi/dns_monkey/releases/download/v0.1.0/dns_monkey-v0.1.0-setup.exe).

<div align="center">
  <img
    src="https://media1.giphy.com/media/ax1EHKnI1HDFSri0Vj/giphy.gif"
    alt="DNS Monkey usage demo"
  >
</div>

## Config
It comes with the following list of resolvers:
| Resolver   | IP 1           | IP 2           |
| ---------- | -------------- | -------------- |
| Cloudflare | 1.1.1.1        | 1.0.0.1        |
| Google     | 8.8.8.8        | 8.8.4.4        |
| Quad 9     | 9.9.9.9        | 49.112.112.112 |
| Quad 9 ECS | 9.9.9.11       | 149.112.112.11 |
| Verisign   | 64.6.64.6      | 64.6.65.6      |
| AdGuard    | 94.140.14.14   | 94.140.15.15   |
| Electro    | 78.157.42.100  | 78.157.42.101  |
| Shecan     | 178.22.122.100 | 185.51.200.2   |
| Begzar     | 185.55.225.25  | 185.55.226.26  |
| Radar      | 10.202.10.10   | 10.202.10.11   |
| 403        | 10.202.10.102  | 10.202.10.202  |

You can also change this list in the config file:
```
%USERPROFILE%\.dns_monkey\config.json
```