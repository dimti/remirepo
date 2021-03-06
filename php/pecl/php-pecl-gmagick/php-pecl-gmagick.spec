# spec file for php-pecl-gmagick
#
# Copyright (c) 2010-2015 Remi Collet
# Copyright (c) 2009-2010 Pavel Alexeev
# License: MIT
# http://opensource.org/licenses/MIT
#
# Please, preserve the changelog entries
#
%{?scl:          %scl_package        php-pecl-gmagick}
%{!?php_inidir:  %global php_inidir  %{_sysconfdir}/php.d}
%{!?__pecl:      %global __pecl      %{_bindir}/pecl}
%{!?__php:       %global __php       %{_bindir}/php}

%global pecl_name  gmagick
%global prever     RC2
%global with_zts   0%{?__ztsphp:1}

Summary:        Provides a wrapper to the GraphicsMagick library
Name:           %{?scl_prefix}php-pecl-%{pecl_name}
Version:        1.1.7
Release:        0.5.%{prever}%{?dist}%{!?nophptag:%(%{__php} -r 'echo ".".PHP_MAJOR_VERSION.".".PHP_MINOR_VERSION;')}
License:        PHP
Group:          Development/Libraries
URL:            http://pecl.php.net/package/%{pecl_name}
Source0:        http://pecl.php.net/get/%{pecl_name}-%{version}%{?prever}.tgz

BuildRoot:      %{_tmppath}/%{name}-%{version}-root-%(%{__id_u} -n)
BuildRequires:  %{?scl_prefix}php-pear
BuildRequires:  %{?scl_prefix}php-devel
BuildRequires:  GraphicsMagick-devel >= 1.2.6

Requires(post): %{__pecl}
Requires(postun): %{__pecl}
Requires:       %{?scl_prefix}php(zend-abi) = %{php_zend_api}
Requires:       %{?scl_prefix}php(api) = %{php_core_api}
%{?_sclreq:Requires: %{?scl_prefix}runtime%{?_sclreq}%{?_isa}}

Provides:       %{?scl_prefix}php-%{pecl_name} = %{version}
Provides:       %{?scl_prefix}php-%{pecl_name}%{?_isa} = %{version}
Provides:       %{?scl_prefix}php-pecl(%{pecl_name}) = %{version}
Provides:       %{?scl_prefix}php-pecl(%{pecl_name})%{?_isa} = %{version}

Conflicts:      %{?scl_prefix}php-pecl-imagick
Conflicts:      %{?scl_prefix}php-magickwand

%if "%{?vendor}" == "Remi Collet" && 0%{!?scl:1}
# Other third party repo stuff
Obsoletes:     php53-pecl-%{pecl_name}
Obsoletes:     php53u-pecl-%{pecl_name}
Obsoletes:     php54-pecl-%{pecl_name}
Obsoletes:     php54w-pecl-%{pecl_name}
%if "%{php_version}" > "5.5"
Obsoletes:     php55u-pecl-%{pecl_name}
Obsoletes:     php55w-pecl-%{pecl_name}
%endif
%if "%{php_version}" > "5.6"
Obsoletes:     php56u-pecl-%{pecl_name}
Obsoletes:     php56w-pecl-%{pecl_name}
%endif
%endif

%if 0%{?fedora} < 20 && 0%{?rhel} < 7
# Filter private shared
%{?filter_provides_in: %filter_provides_in %{_libdir}/.*\.so$}
%{?filter_setup}
%endif


%description
%{pecl_name} is a php extension to create, modify and obtain meta information
of images using the GraphicsMagick API.


%prep
%setup -qc

mv %{pecl_name}-%{version}%{?prever} NTS
cd NTS

extver=$(sed -n '/#define PHP_GMAGICK_VERSION/{s/.* "//;s/".*$//;p}' php_gmagick.h)
if test "x${extver}" != "x%{version}%{?prever}"; then
   : Error: Upstream version is ${extver}, expecting %{version}%{?prever}.
   exit 1
fi
cd ..


# Don't install any font (and test using it)
sed -e '/\.ttf"/d' \
    -e '/gmagickdraw-008-setfont_getfont.phpt/d' \
    -i package.xml

# Create configuration file
cat >%{pecl_name}.ini << 'EOF'
; Enable %{pecl_name} extension module
extension=%{pecl_name}.so
EOF

%if %{with_zts}
# Duplicate build tree for nts/zts
cp -r NTS ZTS
%endif


%build
cd NTS
%{_bindir}/phpize
%{configure} --with-%{pecl_name}  --with-php-config=%{_bindir}/php-config
make %{?_smp_mflags}

%if %{with_zts}
cd ../ZTS
%{_bindir}/zts-phpize
%{configure} --with-%{pecl_name}  --with-php-config=%{_bindir}/zts-php-config
make %{?_smp_mflags}
%endif


%install
rm -rf %{buildroot}

make -C NTS install INSTALL_ROOT=%{buildroot}

# Install XML package description
install -D -m 664 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml

# Drop in the bit of configuration
install -D -m 664 %{pecl_name}.ini %{buildroot}%{php_inidir}/%{pecl_name}.ini

%if %{with_zts}
make -C ZTS install INSTALL_ROOT=%{buildroot}
install -D -m 664 %{pecl_name}.ini %{buildroot}%{php_ztsinidir}/%{pecl_name}.ini
%endif

# Test & Documentation
for i in $(grep 'role="test"' package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 NTS/$i %{buildroot}%{pecl_testdir}/%{pecl_name}/$i
done
for i in $(grep 'role="doc"' package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 NTS/$i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done


%clean
rm -rf %{buildroot}


%post
%{pecl_install} %{pecl_xmldir}/%{name}.xml  >/dev/null || :


%postun
if [ "$1" -eq "0" ]; then
   %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi

%check
%if 0%{?fedora} < 15 && 0%{?rhel} < 5
# Remove know to fail tests (GM font config issue)
# https://bugzilla.redhat.com/783906
rm -f ?TS/tests/gmagick-006-annotateimage.phpt
%endif

: simple module load test for NTS extension
cd NTS
%{__php} --no-php-ini \
    --define extension=%{buildroot}%{php_extdir}/%{pecl_name}.so \
    --modules | grep %{pecl_name}

: upstream test suite for NTS extension
export TEST_PHP_EXECUTABLE=%{__php}
export REPORT_EXIT_STATUS=1
export NO_INTERACTION=1
if ! %{__php} run-tests.php \
    -n -q \
    -d extension=%{buildroot}%{php_extdir}/%{pecl_name}.so
then
  for i in tests/*diff
  do
    echo "---- FAILURE in $i"
    cat $i
    echo -n "\n----"
  done
  exit 1
fi

%if %{with_zts}
: simple module load test for ZTS extension
cd ../ZTS
%{__ztsphp} --no-php-ini \
    --define extension=%{buildroot}%{php_ztsextdir}/%{pecl_name}.so \
    --modules | grep %{pecl_name}

: upstream test suite for ZTS extension
export TEST_PHP_EXECUTABLE=%{__ztsphp}
%{__ztsphp} run-tests.php \
    -n -q \
    -d extension=%{buildroot}%{php_ztsextdir}/%{pecl_name}.so
%endif


%files
%defattr(-,root,root,-)
%doc %{pecl_docdir}/%{pecl_name}
%doc %{pecl_testdir}/%{pecl_name}
%{pecl_xmldir}/%{name}.xml

%config(noreplace) %{php_inidir}/%{pecl_name}.ini
%{php_extdir}/%{pecl_name}.so

%if %{with_zts}
%config(noreplace) %{php_ztsinidir}/%{pecl_name}.ini
%{php_ztsextdir}/%{pecl_name}.so
%endif


%changelog
* Wed Dec 24 2014 Remi Collet <remi@fedoraproject.org> - 1.1.7-0.5.RC2
- Fedora 21 SCL mass rebuild

* Mon Aug 25 2014 Remi Collet <rcollet@redhat.com> - 1.1.7-0.4.RC2
- improve SCL build

* Mon Mar 17 2014 Remi Collet <remi@fedoraproject.org> - 1.1.7-0.3.RC2
- Update to 1.1.7RC2 (beta)

* Mon Mar  3 2014 Remi Collet <remi@fedoraproject.org> - 1.1.7-0.2.RC1
- add upstream patch for PHP 5.6

* Fri Feb 14 2014 Remi Collet <remi@fedoraproject.org> - 1.1.7-0.1.RC1
- Update to 1.1.7RC1 (beta)

* Thu Jan 30 2014 Remi Collet <remi@fedoraproject.org> - 1.1.6-0.3.RC3
- Update to 1.1.6RC3 (beta)

* Sat Dec 14 2013 Remi Collet <remi@fedoraproject.org> - 1.1.6-0.2.RC2
- Update to 1.1.6RC2 (beta)

* Sat Dec 14 2013 Remi Collet <remi@fedoraproject.org> - 1.1.6-0.1.RC1
- Update to 1.1.6RC1 (beta)
- adapt for SCL
- add patch for setStrokeDashArray / getStrokeDashArray

* Tue Nov  5 2013 Remi Collet <RPMS@FamilleCollet.com> - 1.1.5-0.1.RC1
- Update to 1.1.5RC1
- cleanups for Copr

* Sun Oct 20 2013 Remi Collet <RPMS@FamilleCollet.com> - 1.1.4-0.1.RC1
- Update to 1.1.4RC1
- drop merged patches

* Sun Oct 20 2013 Remi Collet <RPMS@FamilleCollet.com> - 1.1.3-0.1.RC1
- Update to 1.1.3RC1
- install doc in pecl doc_dir
- install tests in pecl test_dir
- take care of test results

* Fri Dec 28 2012 Remi Collet <RPMS@FamilleCollet.com> - 1.1.2-0.1.RC1
- Update to 1.1.2RC1
- also provides php-gmagick

* Wed Sep 12 2012 Remi Collet <RPMS@FamilleCollet.com> - 1.1.1-0.1.RC1
- Update to 1.1.1RC1

* Sat Jun 02 2012 Remi Collet <remi@fedoraproject.org> - 1.1.0-0.5.RC3
- Update to 1.1.0RC3

* Sat Jan 21 2012 Remi Collet <remi@fedoraproject.org> - 1.1.0-0.4.RC2
- add patch for getColor options https://bugs.php.net/60829

* Fri Jan 20 2012 Remi Collet <remi@fedoraproject.org> - 1.1.0-0.3.RC2
- build against php 5.4

* Fri Jan 20 2012 Remi Collet <remi@fedoraproject.org> - 1.1.0-0.2.RC2
- Update to 1.1.0RC2
  fix https://bugs.php.net/60807

* Thu Jan 19 2012 Remi Collet <remi@fedoraproject.org> - 1.1.0-0.1.RC1
- Update to 1.1.0RC1

* Mon Dec 05 2011 Remi Collet <remi@fedoraproject.org> - 1.0.10-0.2.b1
- build against php 5.4

* Mon Dec 05 2011 Remi Collet <remi@fedoraproject.org> - 1.0.10-0.1.b1
- Update to 1.0.10b1
- run tests

* Tue Nov 15 2011 Remi Collet <remi@fedoraproject.org> - 1.0.9-0.2.b1
- build against php 5.4
- add patch for php 5.4, see https://bugs.php.net/60308

* Sun Oct 02 2011 Remi Collet <rpms@famillecollet.com> 1.0.9-0.1.b1
- Update to 1.0.9b1
- build zts extension
- clean spec

* Thu May 05 2011 Remi Collet <rpms@famillecollet.com> 1.0.8-0.4.b2
- Update to 1.0.8b2

* Sat Apr 16 2011 Remi Collet <rpms@famillecollet.com> 1.0.8-0.3.b1
- fix build against latest php

* Sun Oct 17 2010 Remi Collet <rpms@famillecollet.com> 1.0.8-0.2.b1
- F-14 build + add Conflicts php-magickwand

* Mon Sep 13 2010 Remi Collet <rpms@famillecollet.com> 1.0.8-0.1.b1
- Update to 1.0.8b1 for remi repo

* Sun Aug 08 2010 Remi Collet <rpms@famillecollet.com> 1.0.7-0.1.b1
- Update to 1.0.7b1 for remi repo
- remove patch for http://pecl.php.net/bugs/17991
- add fix for http://pecl.php.net/bugs/18002

* Sat Aug 07 2010 Remi Collet <rpms@famillecollet.com> 1.0.6-0.1.b1
- Update to 1.0.6b1 for remi repo
- add patch for http://pecl.php.net/bugs/17991

* Mon Jul 26 2010 Remi Collet <rpms@famillecollet.com> 1.0.5-0.1.b1
- Update to 1.0.5b1 for remi repo

* Mon Jul 26 2010 Pavel Alexeev <Pahan@Hubbitus.info> - 1.0.5b1-5
- Update to 1.0.5b1
- Add Conflicts: php-pecl-imagick - BZ#559675

* Sun Jan 31 2010 Pavel Alexeev <Pahan@Hubbitus.info> - 1.0.3b3-4
- Update to 1.0.3b3

* Fri Jan 29 2010 Remi Collet <rpms@famillecollet.com> 1.0.3-0.1.b3
- update to 1.0.3b3

* Tue Nov  3 2009 Pavel Alexeev <Pahan@Hubbitus.info> - 1.0.2b1-3
- Fedora Review started, thanks to Andrew Colin Kissa.
- Remove macros %%{__make} in favour to plain make.
- Add %%{?_smp_mflags} to make.

* Mon Oct 12 2009 Pavel Alexeev <Pahan@Hubbitus.info> - 1.0.2b1-2
- New version 1.0.2b1 - author include license text by my request. Thank you Vito Chin.
- Include LICENSE.

* Fri Oct  2 2009 Pavel Alexeev <Pahan@Hubbitus.info> - 1.0.1b1-1
- Initial release.
- License text absent, but I ask Vito Chin by email to add it into tarball.
