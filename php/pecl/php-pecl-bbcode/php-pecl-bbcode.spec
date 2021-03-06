# spec file for php-pecl-bbcode
#
# Copyright (c) 2011-2015 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/3.0/
#
# Please, preserve the changelog entries
#
%{?scl:          %scl_package        php-pecl-bbcode}
%{!?php_inidir:  %global php_inidir  %{_sysconfdir}/php.d}
%{!?__pecl:      %global __pecl      %{_bindir}/pecl}
%{!?__php:       %global __php       %{_bindir}/php}

%global with_zts  0%{?__ztsphp:1}
%global pecl_name bbcode
%global pre       b1
%if "%{php_version}" < "5.6"
%global ini_name  %{pecl_name}.ini
%else
%global ini_name  40-%{pecl_name}.ini
%endif

Summary:      BBCode parsing Extension
Name:         %{?scl_prefix}php-pecl-bbcode
Version:      1.0.3
Release:      0.7.%{pre}%{?dist}%{!?nophptag:%(%{__php} -r 'echo ".".PHP_MAJOR_VERSION.".".PHP_MINOR_VERSION;')}
# pecl extension is PHP, bbcode2 is BSD, bstrlib (from bstring) is BSD
License:      PHP and BSD
Group:        Development/Languages
URL:          http://pecl.php.net/package/bbcode

Source:       http://pecl.php.net/get/%{pecl_name}-%{version}%{?pre}.tgz

BuildRoot:    %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: %{?scl_prefix}php-devel >= 5.2.0
BuildRequires: %{?scl_prefix}php-pear

Requires(post): %{__pecl}
Requires(postun): %{__pecl}
Requires:     %{?scl_prefix}php(zend-abi) = %{php_zend_api}
Requires:     %{?scl_prefix}php(api) = %{php_core_api}
%{?_sclreq:Requires: %{?scl_prefix}runtime%{?_sclreq}%{?_isa}}

Provides:     %{?scl_prefix}php-pecl(%{pecl_name}) = %{version}%{?pre}
Provides:     %{?scl_prefix}php-pecl(%{pecl_name})%{?_isa} = %{version}%{?pre}
Provides:     %{?scl_prefix}php-%{pecl_name} = %{version}%{?pre}
Provides:     %{?scl_prefix}php-%{pecl_name}%{?_isa} = %{version}%{?pre}

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
# Filter private shared object
%{?filter_provides_in: %filter_provides_in %{php_extdir}/.*\.so$}
%{?filter_setup}
%endif


%description
This is a quick and efficient BBCode Parsing Library.
It provides various tag types, high speed tree based parsing,
callback system, tag position restriction, Smiley Handling,
Subparsing

It will force closing BBCode tags in the good order, and closing
terminating tags at the end of the string this is in order to ensure
HTML Validity in all case.

Documentation: http://php.net/bbcode


%prep 
%setup -c -q

mv %{pecl_name}-%{version}%{?pre} NTS

cd NTS
sed -i -e '/PHP_BBCODE_VERSION/s/1.1.0-dev/1.0.3b1/' php_bbcode.h

extver=$(sed -n '/#define PHP_BBCODE_VERSION/{s/.* "//;s/".*$//;p}' php_bbcode.h)
if test "x${extver}" != "x%{version}%{?pre}"; then
   : Error: Upstream extension version is ${extver}, expecting %{version}%{?pre}.
   exit 1
fi
cd ..

cat > %{ini_name} << 'EOF'
; Enable %{pecl_name} extension module
extension=%{pecl_name}.so
EOF

%if %{with_zts}
# Duplicate source tree for NTS / ZTS build
cp -pr NTS ZTS
%endif


%build
cd NTS
%{_bindir}/phpize
%configure \
    --with-php-config=%{_bindir}/php-config
make %{?_smp_mflags}

%if %{with_zts}
cd ../ZTS
%{_bindir}/zts-phpize
%configure \
    --with-php-config=%{_bindir}/zts-php-config

make %{?_smp_mflags}
%endif


%install
rm -rf %{buildroot}
make  -C NTS install INSTALL_ROOT=%{buildroot}

# Drop in the bit of configuration
install -Dpm 644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}

# Install XML package description
mkdir -p %{buildroot}%{pecl_xmldir}
install -Dpm 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml

%if %{with_zts}
make -C ZTS install INSTALL_ROOT=%{buildroot}

install -D -m 644 %{ini_name} %{buildroot}%{php_ztsinidir}/%{ini_name}
%endif

# Test & Documentation
for i in $(grep 'role="test"' package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 NTS/$i %{buildroot}%{pecl_testdir}/%{pecl_name}/$i
done
for i in $(grep 'role="doc"' package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 NTS/$i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done


%check
cd NTS
: Minimal load test for NTS extension
%{__php} --no-php-ini \
    --define extension=modules/%{pecl_name}.so \
    --modules | grep %{pecl_name}

: Upstream test suite for NTS extension
TEST_PHP_EXECUTABLE=%{__php} \
TEST_PHP_ARGS="-n -d extension=$PWD/modules/%{pecl_name}.so" \
NO_INTERACTION=1 \
REPORT_EXIT_STATUS=1 \
%{__php} -n run-tests.php


%if %{with_zts}
: Minimal load test for ZTS extension
cd ../ZTS
%{__ztsphp} --no-php-ini \
    --define extension=modules/%{pecl_name}.so \
    --modules | grep %{pecl_name}

: Upstream test suite for ZTS extension
TEST_PHP_EXECUTABLE=%{__ztsphp} \
TEST_PHP_ARGS="-n -d extension=$PWD/modules/%{pecl_name}.so" \
NO_INTERACTION=1 \
REPORT_EXIT_STATUS=1 \
%{__ztsphp} -n run-tests.php
%endif


%clean
rm -rf %{buildroot}


%post
%{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :


%postun
if [ $1 -eq 0 ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi


%files
%defattr(-, root, root, -)
%doc %{pecl_testdir}/%{pecl_name}
%doc %{pecl_docdir}/%{pecl_name}
%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{pecl_name}.so
%{pecl_xmldir}/%{name}.xml

%if %{with_zts}
%config(noreplace) %{php_ztsinidir}/%{ini_name}
%{php_ztsextdir}/%{pecl_name}.so
%endif


%changelog
* Wed Dec 24 2014 Remi Collet <remi@fedoraproject.org> - 1.0.3-0.7.b1
- Fedora 21 SCL mass rebuild

* Tue Aug 26 2014 Remi Collet <rcollet@redhat.com> - 1.0.3-0.6.b1
- improve SCL build

* Tue Apr 15 2014 Remi Collet <remi@fedoraproject.org> - 1.0.3-0.5.b1
- add numerical prefix to extension configuration file

* Fri Nov 29 2013 Remi Collet <rcollet@redhat.com> - 1.0.3-0.4.b1
- adapt for SCL

* Sun Nov  3 2013 Remi Collet <remi@fedoraproject.org> - 1.0.3-0.4.b1
- cleaups for Copr
- install doc in pecl doc_dir
- install tests in pecl test_dir
- build ZTS extension

* Thu Jan 24 2013 Remi Collet <remi@fedoraproject.org> - 1.0.3-0.3.b1
- also provides php-bbcode

* Mon Nov 14 2011 Remi Collet <remi@fedoraproject.org> - 1.0.3-0.2.b1
- build against php 5.4

* Wed Oct 05 2011 Remi Collet <remi@fedoraproject.org> 1.0.3-0.1.b1
- initial RPM