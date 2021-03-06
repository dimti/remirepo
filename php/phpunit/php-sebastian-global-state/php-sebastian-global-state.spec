# spec file for php-sebastian-global-state
#
# Copyright (c) 2014-2015 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/3.0/
#
# Please, preserve the changelog entries
#
%global bootstrap    0
%global gh_commit    c7428acdb62ece0a45e6306f1ae85e1c05b09c01
%global gh_short     %(c=%{gh_commit}; echo ${c:0:7})
%global gh_owner     sebastianbergmann
%global gh_project   global-state
%global php_home     %{_datadir}/php/SebastianBergmann
%if %{bootstrap}
%global with_tests   %{?_with_tests:1}%{!?_with_tests:0}
%else
%global with_tests   %{?_without_tests:0}%{!?_without_tests:1}
%endif

Name:           php-sebastian-global-state
Version:        1.0.0
Release:        1%{?dist}
Summary:        Snapshotting of global state

Group:          Development/Libraries
License:        BSD
URL:            https://github.com/%{gh_owner}/%{gh_project}
Source0:        https://github.com/%{gh_owner}/%{gh_project}/archive/%{gh_commit}/%{gh_project}-%{version}.tar.gz

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  php(language) >= 5.3.3
BuildRequires:  %{_bindir}/phpab
%if %{with_tests}
BuildRequires:  %{_bindir}/phpunit
%endif

# from composer.json
#        "php": ">=5.3.3"
Requires:       php(language) >= 5.3.3
# Optional: php-pecl-uopz

Provides:       php-composer(sebastian/global-state) = %{version}


%description
Snapshotting of global state,
factored out of PHPUnit into a stand-alone component.


%prep
%setup -q -n %{gh_project}-%{gh_commit}


%build
# Generate the Autoloader
phpab --output src/autoload.php src

# For the test suite
phpab --basedir tests --output tests/autoload.php tests/_fixture/


%install
rm -rf     %{buildroot}
mkdir -p   %{buildroot}%{php_home}
cp -pr src %{buildroot}%{php_home}/GlobalState


%check
%if %{with_tests}
cat <<EOF | tee bs.php
<?php
require 'SebastianBergmann/GlobalState/autoload.php';
require 'tests/autoload.php';
EOF

phpunit \
  --include-path %{buildroot}%{_datadir}/php \
  --bootstrap bs.php \
  tests
%else
: bootstrap build with test suite disabled
%endif


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc LICENSE README.md composer.json
%dir %{php_home}
%{php_home}/GlobalState


%changelog
* Fri Dec  5 2014 Remi Collet <remi@fedoraproject.org> - 1.0.0-1
- initial package