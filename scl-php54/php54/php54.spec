%global scl_name_base    php
%global scl_name_version 54
%global scl              %{scl_name_base}%{scl_name_version}
%global macrosdir        %(d=%{_rpmconfigdir}/macros.d; [ -d $d ] || d=%{_root_sysconfdir}/rpm; echo $d)
%scl_package %scl

# do not produce empty debuginfo package
%global debug_package %{nil}

Summary:       Package that installs PHP 5.4
Name:          %scl_name
Version:       2.0
Release:       2%{?dist}
Group:         Development/Languages
License:       GPLv2+

Source0:       macros-build
Source1:       README
Source2:       LICENSE

BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: scl-utils-build
BuildRequires: help2man
# Temporary work-around
BuildRequires: iso-codes

Requires:      %{?scl_prefix}php-common%{?_isa} >= 5.4.32
Requires:      %{?scl_prefix}php-cli%{?_isa}
Requires:      %{?scl_prefix}php-pear           >= 1.9.5
Requires:      %{?scl_name}-runtime%{?_isa}      = %{version}-%{release}

%description
This is the main package for %scl Software Collection,
that install PHP 5.4 language.


%package runtime
Summary:   Package that handles %scl Software Collection.
Group:     Development/Languages
Requires:  scl-utils
Provides:  %{?scl_name}-runtime(%{scl_vendor})
Provides:  %{?scl_name}-runtime(%{scl_vendor})%{?_isa}

%description runtime
Package shipping essential scripts to work with %scl Software Collection.


%package build
Summary:   Package shipping basic build configuration
Group:     Development/Languages
Requires:  scl-utils-build
Requires:  %{?scl_name}-runtime%{?_isa}      = %{version}-%{release}

%description build
Package shipping essential configuration macros
to build %scl Software Collection.


%package scldevel
Summary:   Package shipping development files for %scl
Group:     Development/Languages
Requires:  %{?scl_name}-runtime%{?_isa}      = %{version}-%{release}

%description scldevel
Package shipping development files, especially usefull for development of
packages depending on %scl Software Collection.


%prep
%setup -c -T

cat <<EOF | tee enable
export PATH=%{_bindir}:%{_sbindir}\${PATH:+:\${PATH}}
export LD_LIBRARY_PATH=%{_libdir}\${LD_LIBRARY_PATH:+:\${LD_LIBRARY_PATH}}
export MANPATH=%{_mandir}:\${MANPATH}
EOF

# generate rpm macros file for depended collections
cat << EOF | tee scldev
%%scl_%{scl_name_base}         %{scl}
%%scl_prefix_%{scl_name_base}  %{scl_prefix}
EOF

# This section generates README file from a template and creates man page
# from that file, expanding RPM macros in the template file.
cat >README <<'EOF'
%{expand:%(cat %{SOURCE1})}
EOF

# copy the license file so %%files section sees it
cp %{SOURCE2} .


%build
# generate a helper script that will be used by help2man
cat >h2m_helper <<'EOF'
#!/bin/bash
[ "$1" == "--version" ] && echo "%{scl_name} %{version} Software Collection" || cat README
EOF
chmod a+x h2m_helper

# generate the man page
help2man -N --section 7 ./h2m_helper -o %{scl_name}.7


%install
install -D -m 644 enable %{buildroot}%{_scl_scripts}/enable
install -D -m 644 scldev %{buildroot}%{macrosdir}/macros.%{scl_name_base}-scldevel
install -D -m 644 %{scl_name}.7 %{buildroot}%{_mandir}/man7/%{scl_name}.7

%scl_install

# Add the scl_package_override macro
sed -e 's/@SCL@/%{scl}/g' %{SOURCE0} \
  | tee -a %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl}-config

# Move in correct location, if needed
if [ "%{_root_sysconfdir}/rpm" != "%{macrosdir}" ]; then
  mv  %{buildroot}%{_root_sysconfdir}/rpm/macros.%{scl}-config \
      %{buildroot}%{macrosdir}/macros.%{scl}-config
fi


%files


%if 0%{?fedora} < 19 && 0%{?rhel} < 7
%files runtime
%else
%files runtime -f filesystem
%endif
%defattr(-,root,root)
%doc README LICENSE
%scl_files
%{_mandir}/man7/%{scl_name}.*


%files build
%defattr(-,root,root)
%{macrosdir}/macros.%{scl}-config


%files scldevel
%defattr(-,root,root)
%{macrosdir}/macros.%{scl_name_base}-scldevel


%changelog
* Wed Nov 26 2014 Remi Collet <remi@fedoraproject.org> 2.0-2
- add LD_LIBRARY_PATH in enable script for embedded

* Mon Sep  8 2014 Remi Collet <remi@fedoraproject.org> 2.0-1
- provides php54-runtime(remi)
- add _sclreq macro

* Sun Aug 31 2014 Remi Collet <rcollet@redhat.com> 1.0-1
- initial packaging from php55 from rhscl 1.1
- install macro in /usr/lib/rpm/macros.d
- each package requires runtime (for license)

* Mon Mar 31 2014 Honza Horak <hhorak@redhat.com> - 1.1-7
- Fix path typo in README
  Related: #1061455

* Mon Mar 24 2014 Remi Collet <rcollet@redhat.com> 1.1-6
- own locale and man directories, #1074337

* Wed Feb 12 2014 Remi Collet <rcollet@redhat.com> 1.1-5
- avoid empty debuginfo subpackage
- add LICENSE, README and php55.7 man page #1061455
- add scldevel subpackage #1063357

* Mon Jan 20 2014 Remi Collet <rcollet@redhat.com> 1.1-4
- rebuild with latest scl-utils #1054731

* Tue Nov 19 2013 Remi Collet <rcollet@redhat.com> 1.1-2
- fix scl_package_override

* Tue Nov 19 2013 Remi Collet <rcollet@redhat.com> 1.1-1
- build for RHSCL 1.1

* Tue Sep 17 2013 Remi Collet <rcollet@redhat.com> 1-1.5
- add macros.php55-build for scl_package_override

* Fri Aug  2 2013 Remi Collet <rcollet@redhat.com> 1-1
- initial packaging