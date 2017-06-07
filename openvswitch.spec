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

#%%global commit0 bd916d13dbb845746983a6780da772154df647ba
#%%global date 20180219
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

# Enable PIE, bz#955181
%global _hardened_build 1

# RHEL-7 doesn't define _rundir macro yet
# Fedora 15 onwards uses /run as _rundir
%if 0%{!?_rundir:1}
%define _rundir /run
%endif

# FIXME Test "STP - flush the fdb and mdb when topology changed" fails on s390x
%ifarch %{ix86} x86_64 aarch64 ppc64le
%bcond_without check
%else
%bcond_with check
%endif
# option to run kernel datapath tests, requires building as root!
%bcond_with check_datapath_kernel
# option to build with libcap-ng, needed for running OVS as regular user
%bcond_without libcapng
# option to build openvswitch-ovn-docker package
%bcond_with ovn_docker

# Don't use external sphinx (RHV doesn't have optional repositories enabled)
%global external_sphinx 0

Name: openvswitch
Summary: Open vSwitch
Group: System Environment/Daemons daemon/database/utilities
URL: http://www.openvswitch.org/
# Carried over from 2.6.1 CBS builds, introduced to win over 2.6.90
Epoch:   1
Version: 2.9.0
Release: 56%{?commit0:.%{date}git%{shortcommit0}}%{?dist}

# Nearly all of openvswitch is ASL 2.0.  The bugtool is LGPLv2+, and the
# lib/sflow*.[ch] files are SISSL
# datapath/ is GPLv2 (although not built into any of the binary packages)
License: ASL 2.0 and LGPLv2+ and SISSL

%define dpdkver 17.11
%define dpdkdir dpdk
%define dpdksver %(echo %{dpdkver} | cut -d. -f-2)
# NOTE: DPDK does not currently build for s390x
# DPDK on aarch64 and ppc64le is not stable enough to be enabled in FDP
%define dpdkarches x86_64

%if 0%{?commit0:1}
Source: https://github.com/openvswitch/ovs/archive/%{commit0}.tar.gz#/%{name}-%{shortcommit0}.tar.gz
%else
Source: http://openvswitch.org/releases/%{name}-%{version}.tar.gz
%endif
Source10: http://fast.dpdk.org/rel/dpdk-%{dpdkver}.tar.xz

%if ! %{external_sphinx}
%define docutilsver 0.12
%define pygmentsver 1.4
%define sphinxver   1.1.3
Source100: https://pypi.io/packages/source/d/docutils/docutils-%{docutilsver}.tar.gz
Source101: https://pypi.io/packages/source/P/Pygments/Pygments-%{pygmentsver}.tar.gz
Source102: https://pypi.io/packages/source/S/Sphinx/Sphinx-%{sphinxver}.tar.gz
%endif

Source500: configlib.sh
Source501: gen_config_group.sh
Source502: set_config.sh

# Important: source503 is used as the actual copy file
# @TODO: this causes a warning - fix it?
Source504: arm64-armv8a-linuxapp-gcc-config
Source505: ppc_64-power8-linuxapp-gcc-config
Source506: x86_64-native-linuxapp-gcc-config

# The DPDK is designed to optimize througput of network traffic using, among
# other techniques, carefully crafted assembly instructions.  As such it
# needs extensive work to port it to other architectures.
ExclusiveArch: x86_64 aarch64 ppc64le s390x

# dpdk_mach_arch maps between rpm and dpdk arch name, often same as _target_cpu
# dpdk_mach_tmpl is the config template dpdk_mach name, often "native"
# dpdk_mach is the actual dpdk_mach name used in the dpdk make system
%ifarch x86_64
%define dpdk_mach_arch x86_64
%define dpdk_mach_tmpl native
%define dpdk_mach default
%endif
%ifarch aarch64
%define dpdk_mach_arch arm64
%define dpdk_mach_tmpl armv8a
%define dpdk_mach armv8a
%endif
%ifarch ppc64le
%define dpdk_mach_arch ppc_64
%define dpdk_mach_tmpl power8
%define dpdk_mach power8
%endif

%define dpdktarget %{dpdk_mach_arch}-%{dpdk_mach_tmpl}-linuxapp-gcc

# ovs-patches

# OVS (including OVN) backports (0 - 300)

Patch10: 0001-ofproto-dpif-Delete-system-tunnel-interface-when-rem.patch

Patch20: 0001-ovn-Calculate-UDP-checksum-for-DNS-over-IPv6.patch

Patch30: 0001-ofproto-dpif-xlate-translate-action_set-in-clone-act.patch
Patch31: 0002-tests-ofproto-dpif-New-test-for-action_set-after-tra.patch

Patch40: 0001-lib-tc-Handle-error-parsing-action-in-nl_parse_singl.patch
Patch41: 0002-netdev-tc-offloads-Add-support-for-IP-fragmentation.patch
Patch42: 0001-lib-netdev-tc-offloads-Fix-frag-first-later-translat.patch

Patch50: 0001-rhel-don-t-drop-capabilities-when-running-as-root.patch
Patch51: 0001-rhel-Fix-literal-dollar-sign-usage-in-systemd-servic.patch

Patch60: 0001-ovn-Set-router-lifetime-value-for-IPv6-periodic-RA.patch
Patch62: 0001-ovn-Set-proper-Neighbour-Adv-flag-when-replying-for-.patch

Patch70: 0001-python-avoid-useless-JSON-conversion-to-enhance-perf.patch

Patch80: 0001-ovn-controller-Handle-Port_Binding-s-requested-chass.patch

# Bug 1547065
Patch90: 0001-python-Fix-a-double-encoding-attempt-on-an-Unicode-s.patch

# Bug 1575016
Patch100: 0001-netdev-dpdk-Free-mempool-only-when-no-in-use-mbufs.patch 
Patch101: 0001-netdev-dpdk-Add-mempool-reuse-free-debug.patch

# Bug 1576725
Patch110: 0001-ovn-nbctl-Show-gw-chassis-in-decreasing-prio-order.patch

# Bug 1579025
Patch120: 0001-ovn-pacemaker-Fix-promotion-issue-when-the-master-no.patch

# Bug 1578324
Patch130: 0001-netdev-dpdk-don-t-enable-scatter-for-jumbo-RX-suppor.patch
Patch131: 0001-netdev-dpdk-fix-check-for-net_nfp-driver.patch

# Bug 1583011
Patch140: 0001-ovn-do-not-mark-ND-packets-for-conntrack-in-PRE_LB-stage.patch

# Bug 1575929
Patch150: 0001-ovsdb-idl-Correct-singleton-insert-logic.patch

# Bug 1512436
Patch160: 0001-ovs-thread-Fix-thread-id-for-threads-not-started.patch

# DPDK backports (400-700)
# Take patches applied to DPDK 17.11 branch after latest release
# generated with: git diff --src-prefix=a/dpdk-17.11/ \
#                          --dst-prefix=b/dpdk-17.11/ \
#                          v17.11..remotes/origin/17.11
# latest commit included as indicated in patch name
#Patch400:
Patch400: 0001-vhost_user_protect_active_rings_from_async_ring_changes.patch

Patch410: 0001-net-enic-fix-crash-due-to-static-max-number-of-queue.patch
Patch411: 0001-net-enic-fix-L4-Rx-ptype-comparison.patch

Patch420: 0001-vhost-prevent-features-to-be-changed-while-device-is.patch
Patch421: 0002-vhost-propagate-set-features-handling-error.patch
Patch422: 0003-vhost-extract-virtqueue-cleaning-and-freeing-functio.patch
Patch423: 0004-vhost-destroy-unused-virtqueues-when-multiqueue-not-.patch
Patch424: 0005-vhost-add-flag-for-built-in-virtio-driver.patch
Patch425: 0006-vhost-drop-virtqueues-only-with-built-in-virtio-driv.patch
Patch426: 0001-vhost-fix-IOTLB-pool-out-of-memory-handling.patch
Patch427: 0001-vhost-remove-pending-IOTLB-entry-if-miss-request-fai.patch

Patch430: 0001-net-mlx5-use-PCI-address-as-port-name.patch
Patch435: 0001-net-mlx4-fix-broadcast-Rx.patch

# Backport MLX patches to avoid runtime dependencies on rdma-core
# Patches processed with sed -i -e 's@^[-+]\{3\} [ab]@&/dpdk-17.11@' -e '/^diff --git /s@ [ab]/@&dpdk-17.11/@g' mlnx-dpdk-000*
# So autosetup can apply them
Patch451: mlnx-dpdk-0001-net-mlx4-move-rdma-core-calls-to-separate-file.patch
Patch452: mlnx-dpdk-0002-net-mlx4-spawn-rdma-core-dependency-plug-in.patch
Patch453: mlnx-dpdk-0003-net-mlx5-move-rdma-core-calls-to-separate-file.patch
Patch454: mlnx-dpdk-0004-net-mlx5-spawn-rdma-core-dependency-plug-in.patch
Patch455: mlnx-dpdk-0005-net-mlx-add-debug-checks-to-glue-structure.patch
Patch456: mlnx-dpdk-0006-net-mlx-fix-missing-includes-for-rdma-core-glue.patch
Patch457: mlnx-dpdk-0007-net-mlx-version-rdma-core-glue-libraries.patch
Patch458: mlnx-dpdk-0008-net-mlx-make-rdma-core-glue-path-configurable.patch

# Fixes for allowing to run as non-root
Patch459: mlnx-dpdk-0009-net-mlx-control-netdevices-through-ioctl-only.patch

# Backport bnxt patch to fix link down issues when autonegotiation is turned off
Patch460: 0001-net-bnxt-fix-link-speed-setting-with-autoneg-off.patch

# Bug 1559612
Patch465: dpdk-17.11-i40e-fix-link-status-timeout.patch

# QEDE fixes
Patch468: 0001-net-qede-fix-MTU-set-and-max-Rx-length.patch
Patch469: 0001-net-qede-fix-few-log-messages.patch

# Bug 1566712
Patch470: 0001-net-nfp-support-CPP.patch
Patch471: 0002-net-nfp-use-new-CPP-interface.patch
Patch472: 0003-net-nfp-remove-files.patch

# Bug 1567634
Patch475: bnxt-dpdk-0001-net-bnxt-cache-address-of-doorbell-to-subsequent-acc.patch
Patch476: bnxt-dpdk-0002-net-bnxt-avoid-invalid-vnic-id-in-set-L2-Rx-mask.patch
Patch477: bnxt-dpdk-0003-net-bnxt-fix-mbuf-data-offset-initialization.patch

# Bug 1544298
# DPDK CVE-2018-1059 : Information exposure in unchecked guest physical to host virtual address
Patch480: 0001-vhost-fix-indirect-descriptors-table-translation-siz.patch
Patch481: 0002-vhost-check-all-range-is-mapped-when-translating-GPA.patch
Patch482: 0003-vhost-introduce-safe-API-for-GPA-translation.patch
Patch483: 0004-vhost-ensure-all-range-is-mapped-when-translating-QV.patch
Patch484: 0005-vhost-add-support-for-non-contiguous-indirect-descs-.patch
Patch485: 0006-vhost-handle-virtually-non-contiguous-buffers-in-Tx.patch
Patch486: 0007-vhost-handle-virtually-non-contiguous-buffers-in-Rx.patch
Patch487: 0008-vhost-handle-virtually-non-contiguous-buffers-in-Rx-.patch
Patch488: 0009-examples-vhost-move-to-safe-GPA-translation-API.patch
Patch489: 0010-examples-vhost_scsi-move-to-safe-GPA-translation-API.patch
Patch490: 0011-vhost-deprecate-unsafe-GPA-translation-API.patch

# enic fixes
Patch500: 0001-net-enic-allocate-stats-DMA-buffer-upfront-during-pr.patch
Patch501: 0001-net-enic-fix-crash-on-MTU-update-with-non-setup-queu.patch

# Bug 1575067
Patch510: 0001-net-nfp-fix-mbufs-releasing-when-stop-or-close.patch

# Bug 1560728
Patch520: 0001-eal-abstract-away-the-auxiliary-vector.patch
Patch521: 0001-eal-fix-build-with-glibc-2.16.patch
Patch522: 0002-eal-fix-build-on-FreeBSD.patch

# Bug 1552465
Patch530: 0001-vhost-improve-dirty-pages-logging-performance.patch
# Bug 1598752
Patch532: 0001-vhost-fix-missing-increment-of-log-cache-count.patch

# Bug 1583161
Patch540: 0001-net-nfp-configure-default-RSS-reta-table.patch

# Bug 1568301
## Bug 1583670
Patch545: 0001-net-nfp-fix-lock-file-usage.patch
## Bug 1594740
Patch547: 0001-net-nfp-use-generic-PCI-config-access-functions.patch
## Bug 1596324
Patch548: 0001-net-nfp-avoid-sysfs-resource-file-access.patch
Patch549: 0002-net-nfp-avoid-access-to-sysfs-resource0-file.patch

# Bug 1578981
Patch550: 0001-net-qede-fix-L2-handles-used-for-RSS-hash-update.patch

# Bug 1578590
Patch555: 0001-net-qede-fix-unicast-filter-routine-return-code.patch

# Bug 1589866
Patch560: 0001-net-qede-fix-memory-alloc-for-multiple-port-reconfig.patch

# Bug 1581230
Patch570: 0001-net-mlx5-fix-memory-region-cache-lookup.patch
Patch571: 0001-net-mlx5-fix-memory-region-boundary-checks.patch

# Bug 1589264
Patch575: 0001-net-bnxt-fix-set-MTU.patch

# Bug 1618488
Patch590: 0001-vhost-retranslate-vring-addr-when-memory-table-chang.patch

BuildRequires: gcc

# FIXME Sphinx is used to generate some manpages, unfortunately, on RHEL, it's
# in the -optional repository and so we can't require it directly since RHV
# doesn't have the -optional repository enabled and so TPS fails
%if %{external_sphinx}
BuildRequires: python-sphinx
%else
# Sphinx dependencies
BuildRequires: python2-devel >= 2.4
BuildRequires: python-setuptools
#BuildRequires: python-docutils
BuildRequires: python-jinja2
BuildRequires: python-nose
#BuildRequires: python-pygments
# docutils dependencies
BuildRequires: python-imaging
# pygments dependencies
BuildRequires: python-nose
%endif

BuildRequires: autoconf automake libtool
BuildRequires: systemd-units openssl openssl-devel
BuildRequires: python python-six
BuildRequires: desktop-file-utils
BuildRequires: groff-base graphviz
# make check dependencies
BuildRequires: procps-ng
BuildRequires: pyOpenSSL
%if %{with check_datapath_kernel}
BuildRequires: nmap-ncat
# would be useful but not available in RHEL or EPEL
#BuildRequires: pyftpdlib
%endif

%if %{with libcapng}
BuildRequires: libcap-ng libcap-ng-devel
%endif

%ifarch %{dpdkarches}
# DPDK driver dependencies
BuildRequires: zlib-devel numactl-devel
%ifarch x86_64
BuildRequires: rdma-core-devel >= 15
%global __requires_exclude_from ^%{_libdir}/openvswitch/librte_pmd_mlx[45]_glue\.so.*$
%endif

# Virtual provide for depending on DPDK-enabled OVS
Provides: openvswitch-dpdk = %{version}-%{release}
# Migration path for openvswitch-dpdk package
Obsoletes: openvswitch-dpdk < 2.6.0
# Required by packaging policy for the bundled DPDK
Provides: bundled(dpdk) = %{dpdkver}
%endif

Requires: openssl iproute module-init-tools
#Upstream kernel commit 4f647e0a3c37b8d5086214128614a136064110c3
#Requires: kernel >= 3.15.0-0
Requires: openvswitch-selinux-extra-policy

Requires(pre): shadow-utils
Requires(post): /bin/sed
Requires(post): /usr/sbin/usermod
Requires(post): /usr/sbin/groupadd
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units
Obsoletes: openvswitch-controller <= 0:2.1.0-1
%if ! %{with ovn_docker}
Obsoletes: openvswitch-ovn-docker < 2.7.2-2
%endif

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
Provides: openvswitch-static = %{epoch}:%{version}-%{release}

%description devel
This provides static library, libopenswitch.a and the openvswitch header
files needed to build an external application.

%package ovn-central
Summary: Open vSwitch - Open Virtual Network support
License: ASL 2.0
Requires: openvswitch openvswitch-ovn-common
Requires: firewalld-filesystem

%description ovn-central
OVN, the Open Virtual Network, is a system to support virtual network
abstraction.  OVN complements the existing capabilities of OVS to add
native support for virtual network abstractions, such as virtual L2 and L3
overlays and security groups.

%package ovn-host
Summary: Open vSwitch - Open Virtual Network support
License: ASL 2.0
Requires: openvswitch openvswitch-ovn-common
Requires: firewalld-filesystem

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

%if %{with ovn_docker}
%package ovn-docker
Summary: Open vSwitch - Open Virtual Network support
License: ASL 2.0
Requires: openvswitch openvswitch-ovn-common python-openvswitch

%description ovn-docker
Docker network plugins for OVN.
%endif

%prep
%if 0%{?commit0:1}
%autosetup -n ovs-%{commit0} -a 10 -p 1
%else
%autosetup -a 10 -p 1
%endif
%if ! %{external_sphinx}
%if 0%{?commit0:1}
%setup -n ovs-%{commit0} -q -D -T -a 100 -a 101 -a 102
%else
%setup -q -D -T -a 100 -a 101 -a 102
%endif
%endif

%build
# Build Sphinx on RHEL
%if ! %{external_sphinx}
export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}%{_builddir}/pytmp/lib/python"
for x in docutils-%{docutilsver} Pygments-%{pygmentsver} Sphinx-%{sphinxver}; do
    pushd "$x"
    python setup.py install --home %{_builddir}/pytmp
    popd
done

export PATH="$PATH:%{_builddir}/pytmp/bin"
%endif

%if 0%{?commit0:1}
# fix the snapshot unreleased version to be the released one.
sed -i.old -e "s/^AC_INIT(openvswitch,.*,/AC_INIT(openvswitch, %{version},/" configure.ac
%endif
./boot.sh

%ifarch %{dpdkarches}    # build dpdk
# Lets build DPDK first
cd %{dpdkdir}-%{dpdkver}

# In case dpdk-devel is installed
unset RTE_SDK RTE_INCLUDE RTE_TARGET

# Avoid appending second -Wall to everything, it breaks upstream warning
# disablers in makefiles. Strip explicit -march= from optflags since they
# will only guarantee build failures, DPDK is picky with that.
export EXTRA_CFLAGS="$(echo %{optflags} | sed -e 's:-Wall::g' -e 's:-march=[[:alnum:]]* ::g') -Wformat -fPIC"

# DPDK defaults to using builder-specific compiler flags.  However,
# the config has been changed by specifying CONFIG_RTE_MACHINE=default
# in order to build for a more generic host.  NOTE: It is possible that
# the compiler flags used still won't work for all Fedora-supported
# dpdk_machs, but runtime checks in DPDK will catch those situations.

make V=1 O=%{dpdktarget} T=%{dpdktarget} %{?_smp_mflags} config

cp -f %{SOURCE500} %{SOURCE502} "%{_sourcedir}/%{dpdktarget}-config" .
%{SOURCE502} %{dpdktarget}-config "%{dpdktarget}/.config"

make V=1 O=%{dpdktarget} %{?_smp_mflags}

# Generate a list of supported drivers, its hard to tell otherwise.
cat << EOF > README.DPDK-PMDS
DPDK drivers included in this package:

EOF

for f in $(ls %{dpdk_mach_arch}-%{dpdk_mach_tmpl}-linuxapp-gcc/lib/lib*_pmd_*); do
    basename ${f} | cut -c12- | cut -d. -f1 | tr [:lower:] [:upper:]
done >> README.DPDK-PMDS

cat << EOF >> README.DPDK-PMDS

For further information about the drivers, see
http://dpdk.org/doc/guides-%{dpdksver}/nics/index.html
EOF

cd -
%endif    # build dpdk

# And now for OVS...
%ifarch x86_64
LDFLAGS="%{__global_ldflags} -Wl,-rpath,%{_libdir}/openvswitch" \
%endif
%configure \
%if %{with libcapng}
        --enable-libcapng \
%else
        --disable-libcapng \
%endif
        --enable-ssl \
%ifarch %{dpdkarches}
        --with-dpdk=$(pwd)/%{dpdkdir}-%{dpdkver}/%{dpdktarget} \
%endif
        --with-pkidir=%{_sharedstatedir}/openvswitch/pki
/usr/bin/python build-aux/dpdkstrip.py \
        --dpdk \
        < rhel/usr_lib_systemd_system_ovs-vswitchd.service.in \
        > rhel/usr_lib_systemd_system_ovs-vswitchd.service
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

install -d -m 0755 $RPM_BUILD_ROOT%{_rundir}/openvswitch
install -d -m 0750 $RPM_BUILD_ROOT%{_localstatedir}/log/openvswitch
install -d -m 0755 $RPM_BUILD_ROOT%{_sysconfdir}/openvswitch

install -p -D -m 0644 rhel/usr_lib_udev_rules.d_91-vfio.rules \
        $RPM_BUILD_ROOT%{_udevrulesdir}/91-vfio.rules

install -p -D -m 0644 \
        rhel/usr_share_openvswitch_scripts_systemd_sysconfig.template \
        $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/openvswitch

for service in openvswitch ovsdb-server ovs-vswitchd ovs-delete-transient-ports \
                ovn-controller ovn-controller-vtep ovn-northd; do
        install -p -D -m 0644 \
                        rhel/usr_lib_systemd_system_${service}.service \
                        $RPM_BUILD_ROOT%{_unitdir}/${service}.service
done

install -m 0755 rhel/etc_init.d_openvswitch \
        $RPM_BUILD_ROOT%{_datadir}/openvswitch/scripts/openvswitch.init

install -p -D -m 0644 rhel/etc_openvswitch_default.conf \
        $RPM_BUILD_ROOT/%{_sysconfdir}/openvswitch/default.conf

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

install -d -m 0755 $RPM_BUILD_ROOT%{_prefix}/lib/firewalld/services/
install -p -m 0644 rhel/usr_lib_firewalld_services_ovn-central-firewall-service.xml \
        $RPM_BUILD_ROOT%{_prefix}/lib/firewalld/services/ovn-central-firewall-service.xml
install -p -m 0644 rhel/usr_lib_firewalld_services_ovn-host-firewall-service.xml \
        $RPM_BUILD_ROOT%{_prefix}/lib/firewalld/services/ovn-host-firewall-service.xml

install -d -m 0755 $RPM_BUILD_ROOT%{_prefix}/lib/ocf/resource.d/ovn
ln -s %{_datadir}/openvswitch/scripts/ovndb-servers.ocf \
      $RPM_BUILD_ROOT%{_prefix}/lib/ocf/resource.d/ovn/ovndb-servers

install -p -D -m 0755 \
        rhel/usr_share_openvswitch_scripts_ovs-systemd-reload \
        $RPM_BUILD_ROOT%{_datadir}/openvswitch/scripts/ovs-systemd-reload

touch $RPM_BUILD_ROOT%{_sysconfdir}/openvswitch/conf.db
touch $RPM_BUILD_ROOT%{_sysconfdir}/openvswitch/system-id.conf

%ifarch x86_64
install -d -m 0755 $RPM_BUILD_ROOT%{_libdir}/openvswitch
install -p -m 0755 dpdk-%{dpdkver}/%{dpdktarget}/lib/librte_pmd_mlx{4,5}_glue.so.* \
        $RPM_BUILD_ROOT%{_libdir}/openvswitch/
%endif

# remove unpackaged files
rm -f $RPM_BUILD_ROOT/%{_bindir}/ovs-benchmark \
        $RPM_BUILD_ROOT/%{_bindir}/ovs-docker \
        $RPM_BUILD_ROOT/%{_bindir}/ovs-parse-backtrace \
        $RPM_BUILD_ROOT/%{_bindir}/ovs-testcontroller \
        $RPM_BUILD_ROOT/%{_sbindir}/ovs-vlan-bug-workaround \
        $RPM_BUILD_ROOT/%{_mandir}/man1/ovs-benchmark.1* \
        $RPM_BUILD_ROOT/%{_mandir}/man8/ovs-testcontroller.* \
        $RPM_BUILD_ROOT/%{_mandir}/man8/ovs-vlan-bug-workaround.8*

%if %{without ovn_docker}
rm -f $RPM_BUILD_ROOT/%{_bindir}/ovn-docker-overlay-driver \
        $RPM_BUILD_ROOT/%{_bindir}/ovn-docker-underlay-driver
%endif

%check
    export MLX4_GLUE_PATH=$(pwd)/dpdk-%{dpdkver}/%{dpdktarget}/lib
    export MLX5_GLUE_PATH=$(pwd)/dpdk-%{dpdkver}/%{dpdktarget}/lib
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

%pre
getent group openvswitch >/dev/null || groupadd -r openvswitch
getent passwd openvswitch >/dev/null || \
    useradd -r -g openvswitch -d / -s /sbin/nologin \
    -c "Open vSwitch Daemons" openvswitch

%ifarch %{dpdkarches}
    getent group hugetlbfs >/dev/null || groupadd hugetlbfs
    usermod -a -G hugetlbfs openvswitch
%endif
exit 0

%post
if [ $1 -eq 1 ]; then
    sed -i 's:^#OVS_USER_ID=:OVS_USER_ID=:' /etc/sysconfig/openvswitch

%ifarch %{dpdkarches}
    sed -i \
        's@OVS_USER_ID="openvswitch:openvswitch"@OVS_USER_ID="openvswitch:hugetlbfs"@'\
        /etc/sysconfig/openvswitch
%endif
fi
chown -R openvswitch:openvswitch /etc/openvswitch

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
%defattr(-,openvswitch,openvswitch)
%dir %{_sysconfdir}/openvswitch
%{_sysconfdir}/openvswitch/default.conf
%config %ghost %verify(not owner group md5 size mtime) %{_sysconfdir}/openvswitch/conf.db
%ghost %attr(0600,-,-) %verify(not owner group md5 size mtime) %{_sysconfdir}/openvswitch/.conf.db.~lock~
%config %ghost %{_sysconfdir}/openvswitch/system-id.conf
%defattr(-,root,root)
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/sysconfig/openvswitch
%{_sysconfdir}/bash_completion.d/ovs-appctl-bashcomp.bash
%{_sysconfdir}/bash_completion.d/ovs-vsctl-bashcomp.bash
%config(noreplace) %{_sysconfdir}/logrotate.d/openvswitch
%{_unitdir}/openvswitch.service
%{_unitdir}/ovsdb-server.service
%{_unitdir}/ovs-vswitchd.service
%{_unitdir}/ovs-delete-transient-ports.service
%{_datadir}/openvswitch/scripts/openvswitch.init
%{_sysconfdir}/sysconfig/network-scripts/ifup-ovs
%{_sysconfdir}/sysconfig/network-scripts/ifdown-ovs
%{_datadir}/openvswitch/bugtool-plugins/
%{_datadir}/openvswitch/scripts/ovs-bugtool-*
%{_datadir}/openvswitch/scripts/ovs-check-dead-ifs
%{_datadir}/openvswitch/scripts/ovs-lib
%{_datadir}/openvswitch/scripts/ovs-save
%{_datadir}/openvswitch/scripts/ovs-vtep
%{_datadir}/openvswitch/scripts/ovs-ctl
%{_datadir}/openvswitch/scripts/ovs-systemd-reload
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
%ifarch x86_64
%dir %{_libdir}/openvswitch
%{_libdir}/openvswitch/librte_pmd_mlx4_glue.so.*
%{_libdir}/openvswitch/librte_pmd_mlx5_glue.so.*
%endif
%{_sbindir}/ovs-bugtool
%{_sbindir}/ovs-vswitchd
%{_sbindir}/ovsdb-server
%{_mandir}/man1/ovsdb-client.1*
%{_mandir}/man1/ovsdb-server.1*
%{_mandir}/man1/ovsdb-tool.1*
%{_mandir}/man5/ovsdb.5*
%{_mandir}/man5/ovs-vswitchd.conf.db.5*
%{_mandir}/man5/vtep.5*
%{_mandir}/man7/ovsdb-server.7*
%{_mandir}/man7/ovsdb.7*
%{_mandir}/man7/ovs-fields.7*
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
%{_udevrulesdir}/91-vfio.rules
%doc COPYING NOTICE README.rst NEWS rhel/README.RHEL.rst
%ifarch %{dpdkarches}
%doc dpdk-%{dpdkver}/README.DPDK-PMDS
%endif
/var/lib/openvswitch
%attr(750,openvswitch,openvswitch) /var/log/openvswitch
%ghost %attr(755,root,root) %verify(not owner group) %{_rundir}/openvswitch

%if %{with ovn_docker}
%files ovn-docker
%{_bindir}/ovn-docker-overlay-driver
%{_bindir}/ovn-docker-underlay-driver
%endif

%files ovn-common
%{_bindir}/ovn-detrace
%{_bindir}/ovn-nbctl
%{_bindir}/ovn-sbctl
%{_bindir}/ovn-trace
%{_datadir}/openvswitch/scripts/ovn-ctl
%{_datadir}/openvswitch/scripts/ovndb-servers.ocf
%{_datadir}/openvswitch/scripts/ovn-bugtool-nbctl-show
%{_datadir}/openvswitch/scripts/ovn-bugtool-sbctl-lflow-list
%{_datadir}/openvswitch/scripts/ovn-bugtool-sbctl-show
%{_mandir}/man1/ovn-detrace.1*
%{_mandir}/man8/ovn-ctl.8*
%{_mandir}/man8/ovn-nbctl.8*
%{_mandir}/man8/ovn-trace.8*
%{_mandir}/man7/ovn-architecture.7*
%{_mandir}/man8/ovn-sbctl.8*
%{_mandir}/man5/ovn-nb.5*
%{_mandir}/man5/ovn-sb.5*
%{_prefix}/lib/ocf/resource.d/ovn/ovndb-servers

%files ovn-central
%{_bindir}/ovn-northd
%{_mandir}/man8/ovn-northd.8*
%config %{_datadir}/openvswitch/ovn-nb.ovsschema
%config %{_datadir}/openvswitch/ovn-sb.ovsschema
%{_unitdir}/ovn-northd.service
%{_prefix}/lib/firewalld/services/ovn-central-firewall-service.xml

%files ovn-host
%{_bindir}/ovn-controller
%{_mandir}/man8/ovn-controller.8*
%{_unitdir}/ovn-controller.service
%{_prefix}/lib/firewalld/services/ovn-host-firewall-service.xml

%files ovn-vtep
%{_bindir}/ovn-controller-vtep
%{_mandir}/man8/ovn-controller-vtep.8*
%{_unitdir}/ovn-controller-vtep.service

%changelog
* Fri Aug 17 2018 Maxime Coquelin <maxime.coquelin@redhat.com> - 2.9.0-56
- vhost: retranslate vring addr when memory table changes (#1618488)

* Wed Jul 11 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-55
- Fix TPS VerifyTest (rpm -V) by do not verify md5, size and mtime of /etc/sysconfig/openvswitch
  This is needed since /etc/sysconfig/openvswitch is changed in %%post (for DPDK arches).

* Tue Jul 10 2018 Eelco Chaudron <echaudro@redhat.com> - 2.9.0-54
- Backport "Fix thread id for threads not started with ovs_thread_create()" (#1512463)

* Mon Jul 09 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-53
- Backport "ovsdb-idl: Correct singleton insert logic" (#1575929)

* Fri Jul 06 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-52
- Backport "vhost: fix missing increment of log cache count" (#1598752)

* Wed Jul 4 2018 Davide Caratti <dcaratti@redhat.com> - 2.9.0-51
- Backport "net/bnxt: fix set MTU" (#1589264)

* Tue Jul 3 2018 Lorenzo Bianconi <lorenzo.bianconi@redhat.com> - 2.9.0-50
- ovn: Do not mark ND packets for conntrack in PRE_LB stage (#1583011)

* Thu Jun 28 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-49
- Obsoletes openvswitch-ovn-docker < 2.7.2-2 package (#1594404)

* Thu Jun 28 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-48
- Backport "net/nfp: avoid sysfs resource file access" and
  "net/nfp: avoid access to sysfs resource0 file" (#1596324)
- Backport "net/nfp: use generic PCI config access functions" (#1594740)

* Mon Jun 11 2018 Aaron Conole <aconole@redhat.com> - 2.9.0-47
- Backport "net/mlx5: fix memory region cache lookup" (#1581230)
- Backport "net/mlx5: fix memory region boundary checks" (#1581230)

* Mon Jun 11 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-46
- Backport "net/qede: fix memory alloc for multiple port reconfig" (#1589866)

* Thu Jun 07 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-45
- Backport "net/qede: fix unicast filter routine return code" (#1578590)

* Thu Jun 07 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-44
- Backport "net/qede: fix L2-handles used for RSS hash update" (#1578981)

* Tue May 29 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-43
- Backport "net/nfp: fix lock file usage" (#1583670)

* Mon May 28 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-42
- Backport "net/nfp: configure default RSS reta table" (#1583161)

* Mon May 28 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-41
- Backport "netdev-dpdk: don't enable scatter for jumbo RX support for nfp" (#1578324)

* Mon May 28 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-40
- Backport "ovn pacemaker: Fix promotion issue when the master node is reset" (#1579025)

* Thu May 24 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-39
- Backport spec file modfications from "rhel: Use openvswitch user/group for
  the log directory"

* Wed May 23 2018 Maxime Coquelin <maxime.coquelin@redhat.com> - 2.9.0-38
- Backport "vhost: improve dirty pages logging performance" (#1552465)

* Wed May 16 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-37
- Backport "ovn: Set proper Neighbour Adv flag when replying for NS request for
  router IP" (#1567735)

* Mon May 14 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-36
- Enable QEDE PMDs (only on x86_64) (#1578003)

* Thu May 10 2018 Lorenzo Bianconi <lorenzo.bianconi@redhat.com> - 2.9.0-35
- ovn-nbctl: Show gw chassis in decreasing prio order (#1576725)

* Wed May 09 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-34
- Fix hugetlbfs group when DPDK is enabled

* Wed May 09 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-33
- Backport "eal: abstract away the auxiliary vector" (#1560728)
- Re-enable DPDK on ppc64le

* Wed May 09 2018 Aaron Conole <aconole@redhat.com> - 2.9.0-32
- Require the selinux policy module (#1555440)

* Tue May 08 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-31
- Backport fix QEDE PMD (#1494616)

* Tue May 08 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-30
- Backport "net/nfp: fix mbufs releasing when stop or close" (#1575067)

* Sun May 06 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-29
- Backport net/mlx4: fix broadcast Rx (#1568908)

* Fri May 04 2018 Kevin Traynor <ktraynor@redhat.com> - 2.9.0-28
- Backport mempool use after free fix and debug (#1575016)

* Fri May 04 2018 Aaron Conole <aconole@redhat.com> - 2.9.0-27
- Fix the email address in the changelog.

* Wed May 02 2018 Aaron Conole <aconole@redhat.com> - 2.9.0-26
- Backport fix for missing user during install/upgrade (#1559374)

* Mon Apr 30 2018 Jakub Sitnicki <jkbs@redhat.com> - 2.9.0-25
- Backport fix for Unicode encoding in Python IDL (#1547065)

* Thu Apr 26 2018 Aaron Conole <aconole@redhat.com> - 2.9.0-24
- Backport the cisco enic patches

* Thu Apr 26 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-23
- Backport a fix for "Offload of Fragment Matching in OvS Userspace" (#1559111)

* Thu Apr 26 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-22
- Backport "ovn-controller: Handle Port_Binding's "requested-chassis" option" (#1559222)

* Thu Apr 26 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-21
- Backport "python: avoid useless JSON conversion to enhance performance" (#1551016)

* Thu Apr 26 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-20
- Backport "ovn: Set router lifetime value for IPv6 periodic RA" (#1567735)
- Remove useless libpcap-devel dependency

* Mon Apr 23 2018 Kevin Traynor <ktraynor@redhat.com> - 2.9.0-19
- Backport DPDK CVE-2018-1059 (#1544298)

* Fri Apr 20 2018 Davide Caratti <dcaratti@redhat.com> - 2.9.0-18
- Backport fix for PMD segfault when BNXT receives tunneled traffic (#1567634)

* Mon Apr 16 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-17
- Backport patches to make NFP detect the correct firmware (#1566712)
- Backport "rhel: Fix literal dollar sign usage in systemd service files"

* Fri Mar 30 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-16
- Backport "rhel: don't drop capabilities when running as root"
- Change owner of /etc/openvswitch during upgrade

* Tue Mar 27 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-14
- Disable DPDK on ppc64le

* Sun Mar 25 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-13
- Disable DPDK on aarch64

* Thu Mar 22 2018 Flavio Leitner <fbl@redhat.com> - 2.9.0-12
- fixes i40e link status timeout trough direct register access (#1559612)

* Thu Mar 22 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-11
- Enable BNXT, MLX4, MLX5 and NFP (aligned from FDB)

* Thu Mar 22 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-10
- Backport "Offload of Fragment Matching in OvS Userspace" (#1559111)

* Thu Mar 15 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-9
- Avoid to unpack openvswitch 2 times and to overwrite all the patched files
  Fixes 2.9.0-4

* Thu Mar 08 2018 Eric Garver <egarver@redhat.com> - 2.9.0-8
- Backport "ofproto-dpif-xlate: translate action_set in clone action" (#1544892)

* Thu Mar 08 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-7
- Backport "ovn: Calculate UDP checksum for DNS over IPv6" (#1553023)

* Tue Mar 06 2018 Aaron Conole <aconole@redhat.com> - 2.9.0-6
- Require the latest rhel selinux policy (#1549673)

* Fri Mar 02 2018 Matteo Croce <mcroce@redhat.com> - 2.9.0-5
- Backport vhost patches (#1541881)

* Fri Mar 02 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-4
- Don't require python-sphinx directly, but built it since python-sphinx is in
  the optional repository that is not available on RHEV and TPS test fails.

* Tue Feb 20 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-3
- Don't verify the user and group of /etc/openvswitch and /etc/sysconfig/openvswitch
  This is needed since we cannot change the user and group if you upgrade from
  an old version that still uses root:root.

* Tue Feb 20 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.9.0-1
- Update to OVS 2.9.0 + DPDK 17.11 (#1475436)
- Backport of ofproto-dpif: Delete system tunnel interface when remove ovs bridge (#1505776)
- Backport DPDK patches from FDB (vhost user async fix and enic fixes)
- Backport 94cd8383e297 and 951d79e638ec to fix permissions (#1489465)
- Use a static configuration file for DPDK

* Fri Jan 12 2018 Timothy Redaelli <tredaelli@redhat.com> - 2.7.3-3.git20180112
- Rebase to latest OVS branch-2.7 fixes + DPDK 16.11.4 (#1533872)

* Wed Oct 18 2017 Timothy Redaelli <tredaelli@redhat.com> - 2.7.3-2.git20171010
- Remove ovs-test and ovs-vlan-test from openvswitch-test package
- Add an option to enable openvswitch-ovn-docker package (disabled by default)

* Tue Oct 10 2017 Timothy Redaelli <tredaelli@redhat.com> - 2.7.3-1.git20171010
- Update to OVS 2.7.3 + branch-2.7 bugfixes (#1502742)

* Mon Sep 18 2017 Kevin Traynor <ktraynor@redhat.com> - 2.7.2-10.git20170914
- Backport of fix for i40e flow control get (#1491791)

* Thu Sep 14 2017 Timothy Redaelli <tredaelli@redhat.com> - 2.7.2-9.git20170914
- Rebase to latest OVS branch fixes + DPDK 16.11.3

* Wed Sep 06 2017 Timothy Redaelli <tredaelli@redhat.com> - 2.7.2-8.git20170719
- Backport of enic driver crash fix to dpdk-16.11 (#1489010)

* Tue Aug 22 2017 Aaron Conole <aconole@redhat.com> - 2.7.2-7.git20170719
- Re-enable Cisco enic PMD (#1482675)

* Tue Aug 22 2017 Aaron Conole <aconole@redhat.com> - 2.7.2-6.git20170719
- Update based on multi-arch

* Tue Aug 22 2017 Aaron Conole <aconole@redhat.com> - 2.7.2-5.git20170719
- Disable unsupported PMDs (#1482675)
- software and hardware PMDs audited by the team

* Thu Aug 03 2017 John W. Linville <linville@redhat.com> - 2.7.2-4.git20170719
- Backport mmap fix for memory initialization on ppc64le to dpdk-16.11

* Thu Aug 03 2017 John W. Linville <linville@redhat.com> - 2.7.2-3.git20170719
- Backport support for vfio-pci based PMD in ppc64le to dpdk-16.11

* Thu Aug 03 2017 John W. Linville <linville@redhat.com> - 2.7.2-2.git20170719
- Backport support for Intel XL710 (i40e) pmd in ppc64le to dpdk-16.11

* Wed Jul 19 2017 Timothy Redaelli <tredaelli@redhat.com> - 2.7.2-1.git20170719
- Update to OVS 2.7.2 + branch-2.7 bugfixes (#1472854)
- Add a symlink of the OCF script in the OCF resources folder (#1472729)

* Mon Jul 10 2017 Timothy Redaelli <tredaelli@redhat.com> - 2.7.1-1.git20170710
- Align to FDB openvswitch-2.7.1-1.git20170710.el7fdb (#1459286)

* Wed Jun 07 2017 Timothy Redaelli <tredaelli@redhat.com> - 2.6.1-20.git20161206
- backport "mcast-snooping: Avoid segfault for vswitchd" (#1456356)
- backport "mcast-snooping: Flush ports mdb when VLAN cfg changed." (#1456358)

* Sun May 21 2017 Lance Richardson <lrichard@redhat.com> - 2.6.1-19.git20161206
- backport patch to not automatically restard ovn svcs after upgrade (#1438901)

* Tue May 09 2017 Timothy Redaelli <tredaelli@redhat.com> - 2.6.1-18.git20161206
- rconn: Avoid abort for ill-behaved remote (#1449109)

* Fri May 05 2017 Timothy Redaelli <tredaelli@redhat.com> - 2.6.1-17.git20161206
- Fix race in "PMD - change numa node" test (#1447714)
- Report only un-deleted groups in group stats replies. (#1447724)
- Workaround some races in "ofproto - asynchronous message control" tests (#1448536)

* Mon Apr 10 2017 Eric Garver <egarver@redhat.com> - 2.6.1-16.git20161206
- Fix an issue using set_field action on nw_ecn (#1410715)

* Fri Mar 31 2017 Kevin Traynor <ktraynor@redhat.com> - 2.6.1-15.git20161206
- backport patch to fix uni-dir vhost perf drop (#1414919)

* Wed Mar 29 2017 Lance Richardson <lrichard@redhat.com> - 2.6.1-14.git20161206
- backport patch to correct port number in firewalld service file (#1390938)

* Fri Mar 10 2017 Timothy Redaelli <tredaelli@redhat.com> - 2.6.1-13.git20161206
- backport patch to enable/disable libcap-ng support (--with libcapng)

* Thu Mar 09 2017 Aaron Conole <aconole@redhat.com> - 2.6.1-12.git20161206
- Fix an MTU issue with ovs mirror ports (#1426342)

* Wed Mar 08 2017 Lance Richardson <lrichard@redhat.com> - 2.6.1-11.git20161206
- update spec file to install firewalld service files (#1390938)

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

* Mon Feb 06 2017 Flavio Leitner <fbl@redhat.com> 2.5.0-23.git20160727
- fixed broken service after a package upgrade (#1403958)

* Wed Dec 21 2016 Lance Richardson <lrichard@redhat.com> 2.6.1-3.git20161206
- ovsdb-idlc: Initialize nonnull string columns for inserted rows. (#1405094)

* Fri Dec 09 2016 Lance Richardson <lrichard@redhat.com> 2.6.1-2.git20161206
- OVN: Support IPAM with externally specified MAC (#1368043)

* Tue Dec 06 2016 Kevin Traynor <ktraynor@redhat.com> 2.6.1-1.git20161206
- Update to OVS 2.6.1 + branch-2.6 bugfixes (#1335865)
- Update to use DPDK 16.11 (#1335865)
- Enable OVN

* Tue Nov 22 2016 Flavio Leitner <fbl@redhat.com> 2.5.0-22.git20160727
- ifnotifier: do not wake up when there is no db connection (#1397504)

* Tue Nov 22 2016 Flavio Leitner <fbl@redhat.com> 2.5.0-21.git20160727
- Use instant sending instead of queue (#1397481)

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
