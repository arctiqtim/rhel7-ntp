Summary: The NTP daemon and utilities
Name: ntp
Version: 4.2.8p10
Release: 25%{?dist}.2
# primary license (COPYRIGHT) : MIT
# ElectricFence/ (not used) : GPLv2
# kernel/sys/ppsclock.h (not used) : BSD with advertising
# include/ntif.h (not used) : BSD
# include/rsa_md5.h : BSD with advertising
# include/ntp_rfc2553.h : BSD with advertising
# lib/isc/commandline.c (not used) : BSD with advertising
# lib/isc/inet_aton.c (not used) : BSD with advertising
# lib/isc/strtoul.c (not used) : BSD with advertising
# lib/isc/unix/file.c : BSD with advertising
# lib/isc/inet_aton.c (not used) : BSD with advertising
# libntp/mktime.c : BSD with advertising
# libntp/ntp_random.c : BSD with advertising
# libntp/memmove.c : BSD with advertising
# libntp/ntp_rfc2553.c : BSD with advertising
# libntp/adjtimex.c (not used) : BSD
# libparse/ : BSD
# ntpd/refclock_jjy.c: MIT
# ntpd/refclock_oncore.c : BEERWARE License (aka, Public Domain)
# ntpd/refclock_palisade.c : BSD with advertising
# ntpd/refclock_jupiter.c : BSD with advertising
# ntpd/refclock_mx4200.c : BSD with advertising
# ntpd/refclock_palisade.h : BSD with advertising
# ntpstat-0.2/ : GPLv2
# sntp/libopts/ (not used) : BSD or GPLv3+
# util/ansi2knr.c (not used) : GPL+
License: (MIT and BSD and BSD with advertising) and GPLv2
Group: System Environment/Daemons
Source0: ntp-%{version}.tar.gz
Source1: ntp.conf
Source2: ntp.keys
Source4: ntpd.sysconfig
# https://github.com/mlichvar/ntpstat/archive/master.zip
# replaced the old ntpstat with a shell script version that emulates functionality using ntpq
Source5: ntpstat.tgz
Source6: ntp.step-tickers
Source7: ntpdate.wrapper
Source8: ntp.cryptopw
Source9: ntpdate.sysconfig
Source10: ntp.dhclient
Source12: ntpd.service
Source13: ntpdate.service
Source14: ntp-wait.service
Source15: sntp.service
Source16: sntp.sysconfig

URL: http://www.ntp.org
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
Requires: ntpdate = %{version}-%{release}
BuildRequires: libcap-devel openssl-devel libedit-devel perl-HTML-Parser
BuildRequires: pps-tools-devel autogen autogen-libopts-devel systemd-units
BuildRequires: bison

%description
The Network Time Protocol (NTP) is used to synchronize a computer's
time with another reference time source. This package includes ntpd
(a daemon which continuously adjusts system time) and utilities used
to query and configure the ntpd daemon.

Perl scripts ntp-wait and ntptrace are in the ntp-perl package,
ntpdate is in the ntpdate package and sntp is in the sntp package.
The documentation is in the ntp-doc package.

%package perl
Summary: NTP utilities written in Perl
Group: Applications/System
Requires: %{name} = %{version}-%{release}
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
# perl introduced in 4.2.4p4-7
Obsoletes: %{name} < 4.2.4p4-7
BuildArch: noarch
%description perl
This package contains Perl scripts ntp-wait and ntptrace.
 
%package -n ntpdate
Summary: Utility to set the date and time via NTP
Group: Applications/System
Requires(pre): shadow-utils
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

%description -n ntpdate
ntpdate is a program for retrieving the date and time from
NTP servers.

%package -n sntp
Summary: Standard Simple Network Time Protocol program
Group: Applications/System
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

%description -n sntp
sntp can be used as a SNTP client to query a NTP or SNTP server and either
display the time or set the local system's time (given suitable privilege).
It can be run as an interactive command or in a cron job.

%package doc
Summary: NTP documentation
Group: Documentation
Requires: %{name} = %{version}-%{release}
BuildArch: noarch
%description doc
This package contains NTP documentation in HTML format.
 
%global ntpdocdir %{_datadir}/doc/%{name}-%{version}

# pool.ntp.org vendor zone which will be used in ntp.conf
%if 0%{!?vendorzone:1}
%{?fedora: %global vendorzone fedora.}
%{?rhel: %global vendorzone rhel.}
%endif

%prep
%setup -q -a 5

# set default path to sntp KoD database
sed -i 's|/var/db/ntp-kod|%{_localstatedir}/lib/sntp/kod|' sntp/{sntp.1sntpman,sntp.1sntpmdoc,main.c}

# fix line terminators
sed -i 's|\r||g' html/scripts/{footer.txt,style.css}

for f in COPYRIGHT ChangeLog; do
	iconv -f iso8859-1 -t utf8 -o ${f}{_,} && touch -r ${f}{,_} && mv -f ${f}{_,}
done

# don't regenerate texinfo files as it breaks build with _smp_mflags
touch ntpd/ntpd-opts.texi util/ntp-keygen-opts.texi

# autogen fails to regenerate man pages (#958908), but they won't be used anyway
touch ntpd/ntpd.1 util/ntp-keygen.1

# make the build fail if the parsers are not regenerated
rm ntpd/ntp_parser.{c,h}
echo > ntpd/ntp_keyword.h

%build
# sed -i 's|$CFLAGS -Wstrict-overflow|$CFLAGS|' configure sntp/configure
export CFLAGS="$RPM_OPT_FLAGS -fPIE -fno-strict-aliasing -fno-strict-overflow"
export LDFLAGS="-pie -Wl,-z,relro,-z,now"
#%configure 
%configure \
	--sysconfdir=%{_sysconfdir}/ntp/crypto \
	--with-openssl-libdir=%{_libdir} \
	--without-ntpsnmpd \
	--enable-all-clocks --enable-parse-clocks \
	--enable-ntp-signd=%{_localstatedir}/run/ntp_signd 
	# --disable-local-libopts
echo '#define KEYFILE "%{_sysconfdir}/ntp/keys"' >> ntpdate/ntpdate.h
echo '#define NTP_VAR "%{_localstatedir}/log/ntpstats/"' >> config.h

make -C ntpd ntp_keyword.h
make %{?_smp_mflags}

# sed -i 's|$ntpq = "ntpq"|$ntpq = "%{_sbindir}/ntpq"|' scripts/ntptrace
# sed -i 's|ntpq -c |%{_sbindir}/ntpq -c |' scripts/ntp-wait

pushd html
# ../scripts/html2man
# remove adjacent blank lines
# sed -i 's/^[\t\ ]*$//;/./,/^$/!d' man/man*/*.[58]
popd 

## make -C ntpstat-0.2 CFLAGS="$CFLAGS"
## now do not need to build ntpstat

%install
make DESTDIR=$RPM_BUILD_ROOT bindir=%{_sbindir} install

mkdir -p $RPM_BUILD_ROOT%{_mandir}/man{5,8}
# sed -i 's/sntp\.1/sntp\.8/' $RPM_BUILD_ROOT%{_mandir}/man1/sntp.1
# mv $RPM_BUILD_ROOT%{_mandir}/man{1/sntp.1,8/sntp.8}
rm -rf $RPM_BUILD_ROOT%{_mandir}/man1

pushd ntpstat
mkdir -p $RPM_BUILD_ROOT%{_bindir}
install -m 755 ntpstat $RPM_BUILD_ROOT%{_bindir}
install -m 644 ntpstat.1 $RPM_BUILD_ROOT%{_mandir}/man8/ntpstat.8
popd

# fix section numbers
# sed -i 's/\(\.TH[a-zA-Z ]*\)[1-9]\(.*\)/\18\2/' $RPM_BUILD_ROOT%{_mandir}/man8/*.8
# cp -r html/man/man[58] $RPM_BUILD_ROOT%{_mandir}

mkdir -p $RPM_BUILD_ROOT%{ntpdocdir}
cp -p COPYRIGHT ChangeLog NEWS $RPM_BUILD_ROOT%{ntpdocdir}

# prepare html documentation
find html | grep -E '\.(html|css|txt|jpg|gif)$' | grep -v '/build/\|sntp' | \
	cpio -pmd $RPM_BUILD_ROOT%{ntpdocdir}
find $RPM_BUILD_ROOT%{ntpdocdir} -type f | xargs chmod 644
find $RPM_BUILD_ROOT%{ntpdocdir} -type d | xargs chmod 755

pushd $RPM_BUILD_ROOT
mkdir -p .%{_sysconfdir}/{ntp/crypto,sysconfig,dhcp/dhclient.d} .%{_libexecdir}
mkdir -p .%{_localstatedir}/{lib/{s,}ntp,log/ntpstats} .%{_unitdir}
touch .%{_localstatedir}/lib/{ntp/drift,sntp/kod}
sed -e 's|VENDORZONE\.|%{vendorzone}|' \
	-e 's|ETCNTP|%{_sysconfdir}/ntp|' \
	-e 's|VARNTP|%{_localstatedir}/lib/ntp|' \
	< %{SOURCE1} > .%{_sysconfdir}/ntp.conf
touch -r %{SOURCE1} .%{_sysconfdir}/ntp.conf
install -p -m600 %{SOURCE2} .%{_sysconfdir}/ntp/keys
install -p -m755 %{SOURCE7} .%{_libexecdir}/ntpdate-wrapper
install -p -m644 %{SOURCE4} .%{_sysconfdir}/sysconfig/ntpd
install -p -m644 %{SOURCE9} .%{_sysconfdir}/sysconfig/ntpdate
sed -e 's|VENDORZONE\.|%{vendorzone}|' \
	< %{SOURCE6} > .%{_sysconfdir}/ntp/step-tickers
touch -r %{SOURCE6} .%{_sysconfdir}/ntp/step-tickers
sed -e 's|VENDORZONE\.|%{vendorzone}|' \
	< %{SOURCE16} > .%{_sysconfdir}/sysconfig/sntp
touch -r %{SOURCE16} .%{_sysconfdir}/sysconfig/sntp
install -p -m600 %{SOURCE8} .%{_sysconfdir}/ntp/crypto/pw
install -p -m755 %{SOURCE10} .%{_sysconfdir}/dhcp/dhclient.d/ntp.sh
install -p -m644 %{SOURCE12} .%{_unitdir}/ntpd.service
install -p -m644 %{SOURCE13} .%{_unitdir}/ntpdate.service
install -p -m644 %{SOURCE14} .%{_unitdir}/ntp-wait.service
install -p -m644 %{SOURCE15} .%{_unitdir}/sntp.service

mkdir .%{_prefix}/lib/systemd/ntp-units.d
echo 'ntpd.service' > .%{_prefix}/lib/systemd/ntp-units.d/60-ntpd.list

popd

%pre -n ntpdate
/usr/sbin/groupadd -g 38 ntp  2> /dev/null || :
/usr/sbin/useradd -u 38 -g 38 -s /sbin/nologin -M -r -d %{_sysconfdir}/ntp ntp 2>/dev/null || :

%post
%systemd_post ntpd.service

%post -n ntpdate
%systemd_post ntpdate.service

%post -n sntp
%systemd_post sntp.service

%post perl
%systemd_post ntp-wait.service

%preun
%systemd_preun ntpd.service

%preun -n ntpdate
%systemd_preun ntpdate.service

%preun -n sntp
%systemd_preun sntp.service

%preun perl
%systemd_preun ntp-wait.service

%postun
%systemd_postun_with_restart ntpd.service

%postun -n ntpdate
%systemd_postun

%postun -n sntp
%systemd_postun

%postun perl
%systemd_postun

%files
%dir %{ntpdocdir}
%{ntpdocdir}/COPYRIGHT
%{ntpdocdir}/ChangeLog
%{ntpdocdir}/NEWS
%{_sbindir}/ntp-keygen
%{_sbindir}/ntpd
%{_sbindir}/ntpdc
%{_sbindir}/ntpq
%{_sbindir}/ntptime
%{_sbindir}/tickadj
%config(noreplace) %{_sysconfdir}/sysconfig/ntpd
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/ntp.conf
%dir %attr(750,root,ntp) %{_sysconfdir}/ntp/crypto
%config(noreplace) %{_sysconfdir}/ntp/crypto/pw
%dir %{_sysconfdir}/dhcp/dhclient.d
%{_sysconfdir}/dhcp/dhclient.d/ntp.sh
%dir %attr(-,ntp,ntp) %{_localstatedir}/lib/ntp
%ghost %attr(644,ntp,ntp) %{_localstatedir}/lib/ntp/drift
%dir %attr(-,ntp,ntp) %{_localstatedir}/log/ntpstats
%{_bindir}/ntpstat
%{_mandir}/man5/*.5*
%{_mandir}/man8/ntp-keygen.8*
%{_mandir}/man8/ntpd.8*
%{_mandir}/man8/ntpdc.8*
%{_mandir}/man8/ntpq.8*
%{_mandir}/man8/ntpstat.8*
# %{_mandir}/man8/ntptime.8*
# %{_mandir}/man8/tickadj.8*
%{_prefix}/lib/systemd/ntp-units.d/*.list
%{_unitdir}/ntpd.service

%files perl
%{_sbindir}/ntp-wait
%{_sbindir}/ntptrace
%{_mandir}/man8/ntp-wait.8*
%{_mandir}/man8/ntptrace.8*
%{_unitdir}/ntp-wait.service

%files -n ntpdate
%doc COPYRIGHT
%config(noreplace) %{_sysconfdir}/sysconfig/ntpdate
%dir %{_sysconfdir}/ntp
%config(noreplace) %{_sysconfdir}/ntp/keys
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/ntp/step-tickers
%{_libexecdir}/ntpdate-wrapper
%{_sbindir}/ntpdate
# %{_mandir}/man8/ntpdate.8*
%{_unitdir}/ntpdate.service

%files -n sntp
%doc sntp/COPYRIGHT
%config(noreplace) %{_sysconfdir}/sysconfig/sntp
%{_sbindir}/sntp
# %{_mandir}/man8/sntp.8*
%dir %{_localstatedir}/lib/sntp
%ghost %{_localstatedir}/lib/sntp/kod
%{_unitdir}/sntp.service

%files doc
%{ntpdocdir}/html

%changelog


