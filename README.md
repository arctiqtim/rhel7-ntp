# rhel7-ntp

Custom RHEL7 NTP Build

## Installation

This repository can be used to build a custom ntp package.  Ensure you have the proper build tools installed

* yum install rpm-build yum-utils pps-tools-devel perl-HTML-Parser openssl-devel libedit-devel libcap-devel bison autogen autogen-libopts-devel

## Usage

Simply clone the repo, customize the SPEC file if required, and run rpmbuild -bb SPECS/ntp.spec
Install the resulting RPMs

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## Credits

Author - Tim Fairweather, Arctiq
