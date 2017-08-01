# Copyright (C) 2009, 2010, 2013, 2014 Nicira Networks, Inc.
#
# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without warranty of any kind.
#
# If tests have to be skipped while building, specify the '--without check'
# option. For example:
# rpmbuild -bb --without check rhel/openvswitch-fedora.spec

# Enable PIE, bz#955181
%global _hardened_build 1

# RHEL-7 doesn't define _rundir macro yet
# Fedora 15 onwards uses /run as _rundir
%if 0%{!?_rundir:1}
%define _rundir /run
%endif

# run testsuite by default on x86 arches
%ifarch %{ix86} x86_64
%bcond_without check
%else
%bcond_with check
%endif
# option to run kernel datapath tests, requires building as root!
%bcond_with check_datapath_kernel

Name: openvswitch
Summary: Open vSwitch
Group: System Environment/Daemons daemon/database/utilities
URL: http://www.openvswitch.org/
# To win over 2.6.90 build http://cbs.centos.org/koji/buildinfo?buildID=15349
Epoch: 1
Version: 2.6.1

# Nearly all of openvswitch is ASL 2.0.  The bugtool is LGPLv2+, and the
# lib/sflow*.[ch] files are SISSL
# datapath/ is GPLv2 (although not built into any of the binary packages)
License: ASL 2.0 and LGPLv2+ and SISSL

%define snapshot .git20161206
%define rel 10.1%{?snapshot}

#define snapver 10346.git97bab959
%define srcname openvswitch
%define srcver %{version}%{?snapver:-%{snapver}}

%define dpdkver 16.11
%define dpdksver %(echo %{dpdkver} | cut -d. -f-2)
%define dpdktarget %{_arch}-native-linuxapp-gcc

Release: %{?snapver:0.%{snapver}.}%{rel}%{?dist}
Source: http://openvswitch.org/releases/%{srcname}-%{srcver}.tar.gz
Source10: http://dpdk.org/browse/dpdk/snapshot/dpdk-%{dpdkver}.tar.gz

# The DPDK is designed to optimize througput of network traffic using, among
# other techniques, carefully crafted x86 assembly instructions.  As such it
# currently (and likely never will) run on non-x86 platforms.
ExclusiveArch: x86_64

# ovs-patches
# Take patches applied to OVS 2.6 branch after latest release
# generated with: git diff v2.6.1..remotes/origin/branch-2.6
# latest commit included as indicated in patch name
Patch1: openvswitch-2.6-branch-ff22de4f.patch 

# OVS backports
# OVS 2.6 branch uses DPDK 16.07, backport patch to use DPDK 16.11
Patch10: openvswitch-2.6-dpdk16.11-update.patch
# Backport OVN IPAM static MAC support for BZ 1368043
Patch20: ovn-northd-support-IPAM-with-externally-specified-MAC.patch

# Backport for OVN IPAM dhcp renewal request bz 1415449
Patch21: 0001-ovn-Encode-dhcpv6-PACKET_IN-userdata-as-big-endian.patch
Patch22: 0001-ovn-northd-Sort-options-in-put_dhcp-v6-_opts.patch
Patch23: 0001-tests-Fix-race-in-ovn-vtep-3-HVs-1-VIFs-HV-1-GW-1-LS.patch
Patch24: 0001-ovn-northd-Add-flows-in-DHCP_OPTIONS-pipeline-to-sup.patch

# Backport fix for ovn-northd segfault BZ 1405094
Patch30: ovsdb-idlc-Initialize-nonnull-string-columns-for-ins.patch
# Backport OVN checksum option BZ 1418742
Patch40: ovn-controller-Provide-the-option-to-set-Encap.optio.patch

# Backport OVN firewalld configuration files BZ 1390938
Patch41: rhel-firewall-service-files-for-OVN.patch

# Backport make openvswitch service start return when ready BZ 1422227
Patch42: rhel-make-openvswitch-service-start-return-when-read.patch

# Backport ovn-northd ipam: handle the static MAC updates by the user BZ 1418261 
Patch43: ovn-northd-ipam-handle-the-static-MAC-updates-by-the-user.patch

# Backport rhel ifup vhost client mode support BZ 1418957
Patch44: 0001-rhel-ifup-support-vhost-user-client-mode.patch

# Backport rhel-systemd: Restart openvswitch service if a daemon crashes BZ 1468334
Patch50: rhel-systemd-Restart-openvswitch-service-if-a-daemon-crashes.patch

# Backport fix for Avoid segfault for vswitchd BZ 1472334
Patch55: 0001-mcast-snooping-Avoid-segfault-for-vswitchd.patch
# Backport fix for Flush ports mdb when VLAN configuration changed BZ 1472335
Patch56: 0001-mcast-snooping-Flush-ports-mdb-when-VLAN-configurati.patch

# Backport fix to make logs not readable by other BZ 1431490
Patch57: 0001-lib-automake.mk-don-t-install-runtime-directories.patch
Patch58: 0002-rhel-fix-the-fedora-spec.patch
Patch59: 0003-make-logs-not-readable-by-other.patch

Patch60: 0001-rhel-systemd-start-vswitchd-after-udev.patch

Patch61: 0001-netdev-Fix-crash-when-ifa_netmask-is-null.patch
Patch62: ovs-dev-v3-netdev-check-for-NULL-fields-in-netdev_get_addrs.patch

BuildRequires: autoconf automake libtool
BuildRequires: systemd-units openssl openssl-devel
BuildRequires: python python-twisted-core python-zope-interface PyQt4 python-six
BuildRequires: desktop-file-utils
BuildRequires: groff graphviz
# make check dependencies
BuildRequires: procps-ng
%if %{with check_datapath_kernel}
BuildRequires: nmap-ncat
# would be useful but not available in RHEL or EPEL
#BuildRequires: pyftpdlib
%endif

# DPDK driver dependencies
BuildRequires: zlib-devel libpcap-devel numactl-devel

# Virtual provide for depending on DPDK-enabled OVS
Provides: openvswitch-dpdk = %{version}-%{release}
# Migration path for openvswitch-dpdk package
Obsoletes: openvswitch-dpdk < 2.6.0
# Required by packaging policy for the bundled DPDK
Provides: bundled(dpdk) = %{dpdkver}

Requires: openssl iproute module-init-tools
#Upstream kernel commit 4f647e0a3c37b8d5086214128614a136064110c3
#Requires: kernel >= 3.15.0-0

Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
Obsoletes: openvswitch-controller <= 0:2.1.0-1

%description
Open vSwitch provides standard network bridging functions and
support for the OpenFlow protocol for remote per-flow control of
traffic.

%package -n python-openvswitch
Summary: Open vSwitch python bindings
License: ASL 2.0
BuildArch: noarch
Requires: python python-six

%description -n python-openvswitch
Python bindings for the Open vSwitch database

%package test
Summary: Open vSwitch testing utilities
License: ASL 2.0
BuildArch: noarch
Requires: python-openvswitch = %{epoch}:%{version}-%{release}
Requires: python python-twisted-core python-twisted-web

%description test
Utilities that are useful to diagnose performance and connectivity
issues in Open vSwitch setup.

%package devel
Summary: Open vSwitch OpenFlow development package (library, headers)
License: ASL 2.0
Provides: openvswitch-static = %{version}-%{release}

%description devel
This provides static library, libopenswitch.a and the openvswitch header
files needed to build an external application.

%package ovn-central
Summary: Open vSwitch - Open Virtual Network support
License: ASL 2.0
Requires: openvswitch openvswitch-ovn-common

%description ovn-central
OVN, the Open Virtual Network, is a system to support virtual network
abstraction.  OVN complements the existing capabilities of OVS to add
native support for virtual network abstractions, such as virtual L2 and L3
overlays and security groups.

%package ovn-host
Summary: Open vSwitch - Open Virtual Network support
License: ASL 2.0
Requires: openvswitch openvswitch-ovn-common

%description ovn-host
OVN, the Open Virtual Network, is a system to support virtual network
abstraction.  OVN complements the existing capabilities of OVS to add
native support for virtual network abstractions, such as virtual L2 and L3
overlays and security groups.

%package ovn-vtep
Summary: Open vSwitch - Open Virtual Network support
License: ASL 2.0
Requires: openvswitch openvswitch-ovn-common

%description ovn-vtep
OVN vtep controller

%package ovn-common
Summary: Open vSwitch - Open Virtual Network support
License: ASL 2.0
Requires: openvswitch

%description ovn-common
Utilities that are use to diagnose and manage the OVN components.

%package ovn-docker
Summary: Open vSwitch - Open Virtual Network support
License: ASL 2.0
Requires: openvswitch openvswitch-ovn-common python-openvswitch

%description ovn-docker
Docker network plugins for OVN.

%prep
%setup -q -n %{srcname}-%{srcver} -a 10
%patch1 -p1
%patch10 -p1
%patch20 -p1
%patch21 -p1
%patch22 -p1
%patch23 -p1
%patch24 -p1
%patch30 -p1
%patch40 -p1
%patch41 -p1
%patch42 -p1
%patch43 -p1
%patch44 -p1
%patch50 -p1
%patch55 -p1
%patch56 -p1
%patch57 -p1
%patch58 -p1
%patch59 -p1
%patch60 -p1
%patch61 -p1
%patch62 -p1

%build
%if 0%{?snapshot:1}
# fix the snapshot unreleased version to be the released one.
sed -i.old -e "s/^AC_INIT(openvswitch,.*,/AC_INIT(openvswitch, %{version},/" configure.ac
./boot.sh
%endif

# Lets build DPDK first
cd dpdk-%{dpdkver}
function setconf()
{
    cf=%{dpdktarget}/.config
    if grep -q $1 $cf; then
        sed -i "s:^$1=.*$:$1=$2:g" $cf
    else
        echo $1=$2 >> $cf
    fi
}

# In case dpdk-devel is installed
unset RTE_SDK RTE_INCLUDE RTE_TARGET

# Avoid appending second -Wall to everything, it breaks hand-picked
# disablers like per-file -Wno-strict-aliasing
export EXTRA_CFLAGS="`echo %{optflags} | sed -e 's:-Wall::g'` -fPIC -Wno-error"

make V=1 O=%{dpdktarget} T=%{dpdktarget} %{?_smp_mflags} config

# DPDK defaults to optimizing for the builder host we need generic binaries
setconf CONFIG_RTE_MACHINE default

# Disable DPDK libraries not needed by OVS
setconf CONFIG_RTE_LIBRTE_TIMER n
setconf CONFIG_RTE_LIBRTE_CFGFILE n
setconf CONFIG_RTE_LIBRTE_JOBSTATS n
setconf CONFIG_RTE_LIBRTE_LPM n
setconf CONFIG_RTE_LIBRTE_ACL n
setconf CONFIG_RTE_LIBRTE_POWER n
setconf CONFIG_RTE_LIBRTE_DISTRIBUTOR n
setconf CONFIG_RTE_LIBRTE_REORDER n
setconf CONFIG_RTE_LIBRTE_PORT n
setconf CONFIG_RTE_LIBRTE_TABLE n
setconf CONFIG_RTE_LIBRTE_PIPELINE n
setconf CONFIG_RTE_LIBRTE_KNI n
setconf CONFIG_RTE_LIBRTE_CRYPTODEV n

# Enable DPDK libraries needed by OVS
setconf CONFIG_RTE_LIBRTE_VHOST_NUMA y
setconf CONFIG_RTE_LIBRTE_PMD_PCAP y

# Disable PMDs that are either not needed or not stable
setconf CONFIG_RTE_LIBRTE_PMD_VHOST n
setconf CONFIG_RTE_LIBRTE_PMD_NULL_CRYPTO n
# BNX2X driver is not stable
setconf CONFIG_RTE_LIBRTE_BNX2X_PMD n

# Disable virtio user as not used by OVS
setconf CONFIG_RTE_VIRTIO_USER n

# Disable kernel modules
setconf CONFIG_RTE_EAL_IGB_UIO n
setconf CONFIG_RTE_KNI_KMOD n

# Disable experimental stuff
setconf CONFIG_RTE_NEXT_ABI n

# Disable some PMDs on fdProd
setconf CONFIG_RTE_LIBRTE_BNXT_PMD n
setconf CONFIG_RTE_LIBRTE_ENA_PMD n
setconf CONFIG_RTE_LIBRTE_QEDE_PMD n

make V=1 O=%{dpdktarget} %{?_smp_mflags}

# Generate a list of supported drivers, its hard to tell otherwise.
cat << EOF > README.DPDK-PMDS
DPDK drivers included in this package:

EOF

for f in $(ls x86_64-native-linuxapp-gcc/lib/lib*_pmd_*); do
    basename ${f} | cut -c12- | cut -d. -f1 | tr [:lower:] [:upper:]
done >> README.DPDK-PMDS

cat << EOF >> README.DPDK-PMDS

For further information about the drivers, see
http://dpdk.org/doc/guides-%{dpdksver}/nics/index.html
EOF

cd -

# And now for OVS...
autoreconf -i

%configure --enable-ssl --with-pkidir=%{_sharedstatedir}/openvswitch/pki \
           --with-dpdk=$(pwd)/dpdk-%{dpdkver}/%{dpdktarget}
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

install -d -m 0755 $RPM_BUILD_ROOT%{_sysconfdir}/openvswitch

install -p -D -m 0644 \
        rhel/usr_share_openvswitch_scripts_systemd_sysconfig.template \
        $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/openvswitch

for service in openvswitch ovsdb-server ovs-vswitchd \
                ovn-controller ovn-controller-vtep ovn-northd; do
        install -p -D -m 0644 \
                        rhel/usr_lib_systemd_system_${service}.service \
                        $RPM_BUILD_ROOT%{_unitdir}/${service}.service
done

install -m 0755 rhel/etc_init.d_openvswitch \
        $RPM_BUILD_ROOT%{_datadir}/openvswitch/scripts/openvswitch.init

install -p -D -m 0644 rhel/etc_logrotate.d_openvswitch \
        $RPM_BUILD_ROOT/%{_sysconfdir}/logrotate.d/openvswitch

install -m 0644 vswitchd/vswitch.ovsschema \
        $RPM_BUILD_ROOT/%{_datadir}/openvswitch/vswitch.ovsschema

install -d -m 0755 $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/network-scripts/
install -p -m 0755 rhel/etc_sysconfig_network-scripts_ifdown-ovs \
        $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/network-scripts/ifdown-ovs
install -p -m 0755 rhel/etc_sysconfig_network-scripts_ifup-ovs \
        $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/network-scripts/ifup-ovs

install -d -m 0755 $RPM_BUILD_ROOT%{python_sitelib}
mv $RPM_BUILD_ROOT/%{_datadir}/openvswitch/python/* \
   $RPM_BUILD_ROOT%{python_sitelib}
rmdir $RPM_BUILD_ROOT/%{_datadir}/openvswitch/python/

install -d -m 0755 $RPM_BUILD_ROOT/%{_sharedstatedir}/openvswitch

touch $RPM_BUILD_ROOT%{_sysconfdir}/openvswitch/conf.db
touch $RPM_BUILD_ROOT%{_sysconfdir}/openvswitch/system-id.conf

# remove unpackaged files
rm -f $RPM_BUILD_ROOT/%{_bindir}/ovs-benchmark \
        $RPM_BUILD_ROOT/%{_bindir}/ovs-docker \
        $RPM_BUILD_ROOT/%{_bindir}/ovs-parse-backtrace \
        $RPM_BUILD_ROOT/%{_bindir}/ovs-testcontroller \
        $RPM_BUILD_ROOT/%{_sbindir}/ovs-vlan-bug-workaround \
        $RPM_BUILD_ROOT/%{_mandir}/man1/ovs-benchmark.1* \
        $RPM_BUILD_ROOT/%{_mandir}/man8/ovs-testcontroller.* \
        $RPM_BUILD_ROOT/%{_mandir}/man8/ovs-vlan-bug-workaround.8* \
        $RPM_BUILD_ROOT/%{_datadir}/openvswitch/scripts/ovs-save

%check
%if %{with check}
    if make check TESTSUITEFLAGS='%{_smp_mflags}' ||
       make check TESTSUITEFLAGS='--recheck'; then :;
    else
        cat tests/testsuite.log
        exit 1
    fi
%endif
%if %{with check_datapath_kernel}
    if make check-kernel RECHECK=yes; then :;
    else
        cat tests/system-kmod-testsuite.log
        exit 1
    fi
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%preun
%if 0%{?systemd_preun:1}
    %systemd_preun %{name}.service
%else
    if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
        /bin/systemctl --no-reload disable %{name}.service >/dev/null 2>&1 || :
        /bin/systemctl stop %{name}.service >/dev/null 2>&1 || :
    fi
%endif

%preun ovn-central
%if 0%{?systemd_preun:1}
    %systemd_preun ovn-northd.service
%else
    if [ $1 -eq 0 ] ; then
        # Package removal, not upgrade
        /bin/systemctl --no-reload disable ovn-northd.service >/dev/null 2>&1 || :
        /bin/systemctl stop ovn-northd.service >/dev/null 2>&1 || :
    fi
%endif

%preun ovn-host
%if 0%{?systemd_preun:1}
    %systemd_preun ovn-controller.service
%else
    if [ $1 -eq 0 ] ; then
        # Package removal, not upgrade
        /bin/systemctl --no-reload disable ovn-controller.service >/dev/null 2>&1 || :
        /bin/systemctl stop ovn-controller.service >/dev/null 2>&1 || :
    fi
%endif

%preun ovn-vtep
%if 0%{?systemd_preun:1}
    %systemd_preun ovn-controller-vtep.service
%else
    if [ $1 -eq 0 ] ; then
        # Package removal, not upgrade
        /bin/systemctl --no-reload disable ovn-controller-vtep.service >/dev/null 2>&1 || :
        /bin/systemctl stop ovn-controller-vtep.service >/dev/null 2>&1 || :
    fi
%endif

%post
%if 0%{?systemd_post:1}
    %systemd_post %{name}.service
%else
    # Package install, not upgrade
    if [ $1 -eq 1 ]; then
        /bin/systemctl daemon-reload >dev/null || :
    fi
%endif

%post ovn-central
%if 0%{?systemd_post:1}
    %systemd_post ovn-northd.service
%else
    # Package install, not upgrade
    if [ $1 -eq 1 ]; then
        /bin/systemctl daemon-reload >dev/null || :
    fi
%endif

%post ovn-host
%if 0%{?systemd_post:1}
    %systemd_post ovn-controller.service
%else
    # Package install, not upgrade
    if [ $1 -eq 1 ]; then
        /bin/systemctl daemon-reload >dev/null || :
    fi
%endif

%post ovn-vtep
%if 0%{?systemd_post:1}
    %systemd_post ovn-controller-vtep.service
%else
    # Package install, not upgrade
    if [ $1 -eq 1 ]; then
        /bin/systemctl daemon-reload >dev/null || :
    fi
%endif
%postun ovn-central
%if 0%{?systemd_postun_with_restart:1}
    %systemd_postun_with_restart ovn-northd.service
%else
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
    if [ "$1" -ge "1" ] ; then
    # Package upgrade, not uninstall
        /bin/systemctl try-restart ovn-northd.service >/dev/null 2>&1 || :
    fi
%endif

%postun ovn-host
%if 0%{?systemd_postun_with_restart:1}
    %systemd_postun_with_restart ovn-controller.service
%else
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
    if [ "$1" -ge "1" ] ; then
        # Package upgrade, not uninstall
        /bin/systemctl try-restart ovn-controller.service >/dev/null 2>&1 || :
    fi
%endif

%postun ovn-vtep
%if 0%{?systemd_postun_with_restart:1}
    %systemd_postun_with_restart ovn-controller-vtep.service
%else
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
    if [ "$1" -ge "1" ] ; then
        # Package upgrade, not uninstall
        /bin/systemctl try-restart ovn-controller-vtep.service >/dev/null 2>&1 || :
    fi
%endif

%postun
%if 0%{?systemd_postun:1}
    %systemd_postun %{name}.service
%else
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
%endif

%triggerun -- openvswitch < 2.5.0-22.git20160727%{?dist}
# old rpm versions restart the service in postun, but
# due to systemd some preparation is needed.
if systemctl is-active openvswitch >/dev/null 2>&1 ; then
    /usr/share/openvswitch/scripts/ovs-ctl stop >/dev/null 2>&1 || :
    systemctl daemon-reload >/dev/null 2>&1 || :
    systemctl stop openvswitch ovsdb-server ovs-vswitchd >/dev/null 2>&1 || :
    systemctl start openvswitch >/dev/null 2>&1 || :
fi
exit 0

%files -n python-openvswitch
%{python_sitelib}/ovs
%doc COPYING

%files test
%{_bindir}/ovs-test
%{_bindir}/ovs-vlan-test
%{_bindir}/ovs-l3ping
%{_bindir}/ovs-pcap
%{_bindir}/ovs-tcpdump
%{_bindir}/ovs-tcpundump
%{_mandir}/man8/ovs-test.8*
%{_mandir}/man8/ovs-vlan-test.8*
%{_mandir}/man8/ovs-l3ping.8*
%{_mandir}/man1/ovs-pcap.1*
%{_mandir}/man8/ovs-tcpdump.8*
%{_mandir}/man1/ovs-tcpundump.1*
%{python_sitelib}/ovstest

%files devel
%{_libdir}/*.a
%{_libdir}/*.la
%{_libdir}/pkgconfig/*.pc
%{_includedir}/openvswitch/*
%{_includedir}/openflow/*
%{_includedir}/ovn/*

%files
%defattr(-,root,root)
%{_sysconfdir}/bash_completion.d/ovs-appctl-bashcomp.bash
%{_sysconfdir}/bash_completion.d/ovs-vsctl-bashcomp.bash
%dir %{_sysconfdir}/openvswitch
%config %ghost %{_sysconfdir}/openvswitch/conf.db
%config %ghost %{_sysconfdir}/openvswitch/system-id.conf
%config(noreplace) %{_sysconfdir}/sysconfig/openvswitch
%config(noreplace) %{_sysconfdir}/logrotate.d/openvswitch
%{_unitdir}/openvswitch.service
%{_unitdir}/ovsdb-server.service
%{_unitdir}/ovs-vswitchd.service
%{_datadir}/openvswitch/scripts/openvswitch.init
%{_sysconfdir}/sysconfig/network-scripts/ifup-ovs
%{_sysconfdir}/sysconfig/network-scripts/ifdown-ovs
%{_datadir}/openvswitch/bugtool-plugins/
%{_datadir}/openvswitch/scripts/ovs-bugtool-*
%{_datadir}/openvswitch/scripts/ovs-check-dead-ifs
%{_datadir}/openvswitch/scripts/ovs-lib
%{_datadir}/openvswitch/scripts/ovs-vtep
%{_datadir}/openvswitch/scripts/ovs-ctl
%config %{_datadir}/openvswitch/vswitch.ovsschema
%config %{_datadir}/openvswitch/vtep.ovsschema
%{_bindir}/ovs-appctl
%{_bindir}/ovs-dpctl
%{_bindir}/ovs-dpctl-top
%{_bindir}/ovs-ofctl
%{_bindir}/ovs-vsctl
%{_bindir}/ovsdb-client
%{_bindir}/ovsdb-tool
%{_bindir}/ovs-pki
%{_bindir}/vtep-ctl
%{_sbindir}/ovs-bugtool
%{_sbindir}/ovs-vswitchd
%{_sbindir}/ovsdb-server
%{_mandir}/man1/ovsdb-client.1*
%{_mandir}/man1/ovsdb-server.1*
%{_mandir}/man1/ovsdb-tool.1*
%{_mandir}/man5/ovs-vswitchd.conf.db.5*
%{_mandir}/man5/vtep.5*
%{_mandir}/man8/vtep-ctl.8*
%{_mandir}/man8/ovs-appctl.8*
%{_mandir}/man8/ovs-bugtool.8*
%{_mandir}/man8/ovs-ctl.8*
%{_mandir}/man8/ovs-dpctl.8*
%{_mandir}/man8/ovs-dpctl-top.8*
%{_mandir}/man8/ovs-ofctl.8*
%{_mandir}/man8/ovs-pki.8*
%{_mandir}/man8/ovs-vsctl.8*
%{_mandir}/man8/ovs-vswitchd.8*
%{_mandir}/man8/ovs-parse-backtrace.8*
%doc COPYING DESIGN.md INSTALL.SSL.md NOTICE README.md WHY-OVS.md
%doc FAQ.md NEWS INSTALL.DPDK.md rhel/README.RHEL
%doc dpdk-%{dpdkver}/README.DPDK-PMDS
/var/lib/openvswitch
/var/log/openvswitch
%ghost %attr(755,root,root) %{_rundir}/openvswitch

%files ovn-docker
%{_bindir}/ovn-docker-overlay-driver
%{_bindir}/ovn-docker-underlay-driver

%files ovn-common
%{_bindir}/ovn-nbctl
%{_bindir}/ovn-sbctl
%{_bindir}/ovn-trace
%{_datadir}/openvswitch/scripts/ovn-ctl
%{_datadir}/openvswitch/scripts/ovn-bugtool-nbctl-show
%{_datadir}/openvswitch/scripts/ovn-bugtool-sbctl-lflow-list
%{_datadir}/openvswitch/scripts/ovn-bugtool-sbctl-show
%{_mandir}/man8/ovn-ctl.8*
%{_mandir}/man8/ovn-nbctl.8*
%{_mandir}/man8/ovn-trace.8*
%{_mandir}/man7/ovn-architecture.7*
%{_mandir}/man8/ovn-sbctl.8*
%{_mandir}/man5/ovn-nb.5*
%{_mandir}/man5/ovn-sb.5*

%files ovn-central
%{_bindir}/ovn-northd
%{_mandir}/man8/ovn-northd.8*
%config %{_datadir}/openvswitch/ovn-nb.ovsschema
%config %{_datadir}/openvswitch/ovn-sb.ovsschema
%{_unitdir}/ovn-northd.service

%files ovn-host
%{_bindir}/ovn-controller
%{_mandir}/man8/ovn-controller.8*
%{_unitdir}/ovn-controller.service

%files ovn-vtep
%{_bindir}/ovn-controller-vtep
%{_mandir}/man8/ovn-controller-vtep.8*
%{_unitdir}/ovn-controller-vtep.service

%changelog
* Tue Aug 01 2017 Timothy Redaelli <tredaelli@redhat.com> - 2.6.1-10.1.git20161206
- Backport patch to fix random crashes when adding/removing interfaces (#1473735)
- Restart openvswitch service if a daemon crashes (#1468334)
- Avoid segfault for vswitchd (#1472334)
- Flush ports mdb when VLAN configuration changed (#1472335)
- Make logs not readable by other (#1431490)
- Fix ovs-vswitchd start order (#1468751)

* Thu Feb 16 2017 Aaron Conole <aconole@redhat.com> - 2.6.1-10.git20161206
- vhostuser client mode support for ifup/ifdown (#1418957)

* Thu Feb 16 2017 Lance Richardson <lrichard@redhat.com> - 2.6.1-9.git20161206
-  OVN-DHCP is not sending DHCP responses after a MAC change in north db (#1418261)

* Thu Feb 16 2017 Timothy Redaelli <tredaelli@redhat.com> - 2.6.1-8.git20161206
- systemd service starts too fast (#1422227)

* Fri Feb 10 2017 Lance Richardson <lrichard@redhat.com> - 2.6.1-7.git20161206
- iptables should be easily configurable for OVN hosts and OVN central server (#1390938)

* Thu Feb 09 2017 Aaron Conole <aconole@redhat.com> - 2.6.1-6.git20161206
- ovn: IPAM has no reply to DHCP request for renewal (#1415449)

* Tue Feb 07 2017 Timothy Redaelli <tredaelli@redhat.com> - 2.6.1-5.git20161206
- ovn-controller: Provide the option to set Encap.options:csum (#1418742)

* Mon Feb 06 2017 Flavio Leitner <fbl@redhat.com> 2.6.1-4.git20161206
- fixed broken service after a package upgrade (#1419632)

* Wed Dec 21 2016 Lance Richardson <lrichard@redhat.com> 2.6.1-3.git20161206
- ovsdb-idlc: Initialize nonnull string columns for inserted rows. (#1405094)

* Fri Dec 09 2016 Lance Richardson <lrichard@redhat.com> 2.6.1-2.git20161206
- OVN: Support IPAM with externally specified MAC (#1368043)

* Tue Dec 06 2016 Kevin Traynor <ktraynor@redhat.com> 2.6.1-1.git20161206
- Update to OVS 2.6.1 + branch-2.6 bugfixes (#1335865)
- Update to use DPDK 16.11 (#1335865)
- Enable OVN

* Mon Nov 28 2016 Kevin Traynor <ktraynor@redhat.com> 2.5.0-23.git20160727
- dpdk vhost: check ring descriptor address (#1397197)

* Tue Nov 22 2016 Flavio Leitner <fbl@redhat.com> 2.5.0-22.git20160727
- ifnotifier: do not wake up when there is no db connection (#1386514)

* Tue Nov 22 2016 Flavio Leitner <fbl@redhat.com> 2.5.0-21.git20160727
- Use instant sending instead of queue (#1344787)

* Mon Nov 21 2016 Flavio Leitner <fbl@redhat.com> 2.5.0-20.git20160727
- dpdk vhost: workaround stale vring base (#1376217)

* Thu Oct 20 2016 Aaron Conole <aconole@redhat.com> - 2.5.0-19.git20160727
- Applied tnl fix (#1346232)

* Tue Oct 18 2016 Aaron Conole <aconole@redhat.com> - 2.5.0-18.git20160727
- Applied the systemd backports

* Tue Oct 18 2016 Flavio Leitner <fbl@redhat.com> - 2.5.0-17.git20160727
- Fixed OVS to not require SSSE3 if DPDK is not used (#1378501)

* Tue Oct 18 2016 Flavio Leitner <fbl@redhat.com> - 2.5.0-16.git20160727
- Fixed a typo (#1385096)

* Tue Oct 18 2016 Flavio Leitner <fbl@redhat.com> - 2.5.0-15.git20160727
- Do not restart the service after a package upgrade (#1385096)

* Mon Sep 26 2016 Panu Matilainen <pmatilai@redhat.com> - 2.5.0-14.git20160727
- Permit running just the kernel datapath tests (#1375660)

* Wed Sep 14 2016 Panu Matilainen <pmatilai@redhat.com> - 2.5.0-13.git20160727
- Obsolete openvswitch-dpdk < 2.6.0 to provide migration path
- Add spec option to run kernel datapath tests (#1375660)

* Fri Sep 09 2016 Panu Matilainen <pmatilai@redhat.com> - 2.5.0-12.git20160727
- Backport ovs-tcpdump support (#1335560)
- Add ovs-pcap, ovs-tcpdump and ovs-tcpundump to -test package

* Thu Sep 08 2016 Panu Matilainen <pmatilai@redhat.com> - 2.5.0-11.git20160727
- Add openvswitch-dpdk provide for testing and depending on dpdk-enablement
- Disable bnx2x driver, it's not stable
- Build dpdk with -Wno-error to permit for newer compilers
- Drop subpkgs conditional from spec, its not useful anymore

* Fri Aug 26 2016 Panu Matilainen <pmatilai@redhat.com> - 2.5.0-10.git20160727
- Fix adding ukeys for same flow by different pmds (#1364898)

* Thu Jul 28 2016 Flavio Leitner <fbl@redhat.com> - 2.5.0-9.git20160727
- Fixed ifup-ovs to support DPDK Bond (#1360426)

* Thu Jul 28 2016 Flavio Leitner <fbl@redhat.com> - 2.5.0-8.git20160727
- Fixed ifup-ovs to delete the ports first (#1359890)

* Wed Jul 27 2016 Flavio Leitner <fbl@redhat.com> - 2.5.0-7.git20160727
- pull bugfixes from upstream 2.5 branch (#1360431)

* Tue Jul 26 2016 Flavio Leitner <fbl@redhat.com> - 2.5.0-6.git20160628
- Removed redundant provides for openvswitch
- Added epoch to the provides for -static package

* Thu Jul 21 2016 Flavio Leitner <fbl@redhat.com> - 2.5.0-5.git20160628
- Renamed to openvswitch (dpdk enabled)
- Enabled sub-packages
- Removed conflicts to openvswitch
- Increased epoch to give this package preference over stable

* Tue Jun 28 2016 Panu Matilainen <pmatilai@redhat.com> - 2.5.0-4.git20160628
- pull bugfixes from upstream 2.5 branch (#1346313)

* Wed Apr 27 2016 Panu Matilainen <pmatilai@redhat.com> - 2.5.0-4
- Enable DPDK bnx2x driver (#1330589)
- Add README.DPDK-PMDS document listing drivers included in this package

* Thu Mar 17 2016 Flavio Leitner <fbl@redhat.com> - 2.5.0-3
- Run testsuite by default on x86 arches (#1318786)
  (this sync the spec with non-dpdk version though the testsuite
   was already enabled here)

* Thu Mar 17 2016 Panu Matilainen <pmatilai@redhat.com> - 2.5.0-2
- eliminate debuginfo-artifacts (#1281913)

* Thu Mar 17 2016 Panu Matilainen <pmatilai@redhat.com> - 2.5.0-1
- Update to OVS to 2.5.0 and bundled DPDK to 2.2.0 (#1317889)

* Mon Nov 23 2015 Panu Matilainen <pmatilai@redhat.com>
- Provide openvswitch ver-rel (#1281894)

* Thu Aug 13 2015 Flavio Leitner <fbl@redhat.com>
- ExclusiveArch to x86_64 (dpdk)
- Provides bundled(dpdk)
- Re-enable testsuite

* Fri Aug 07 2015 Panu Matilainen <pmatilai@redhat.com>
- Enable building from pre-release snapshots, update to pre 2.4 version
- Bundle a minimal, private build of DPDK 2.0 and link statically
- Rename package to openvswitch-dpdk, conflict with regular openvswitch
- Disable all sub-packages

* Wed Jan 12 2011 Ralf Spenneberg <ralf@os-s.net>
- First build on F14
