%global github_owner    nikic
%global github_name     PHP-Parser
%global github_version  1.0.2
%global github_commit   a8ffc6fcfcbae268656c8acf1298e378ac1ee5f1

%global lib_name        PhpParser
%global lib_name_old    PHPParser

%global php_min_ver     5.3

Name:          php-%{lib_name_old}
Version:       %{github_version}
Release:       1%{?dist}
Summary:       A PHP parser written in PHP

Group:         Development/Libraries
License:       BSD
URL:           https://github.com/%{github_owner}/%{github_name}
Source0:       %{url}/archive/%{github_commit}/%{name}-%{github_version}-%{github_commit}.tar.gz

BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:     noarch
# For tests
BuildRequires: php(language) >= %{php_min_ver}
BuildRequires: %{_bindir}/phpunit
# For tests: phpcompatinfo (computed from version 1.0.2)
BuildRequires: php-ctype
BuildRequires: php-filter
BuildRequires: php-pcre
BuildRequires: php-spl
BuildRequires: php-tokenizer
BuildRequires: php-xmlreader
BuildRequires: php-xmlwriter

# composer.json
Requires:      php(language) >= %{php_min_ver}
Requires:      php-tokenizer
# phpcompatinfo (computed from version 1.0.2)
Requires:      php-filter
Requires:      php-pcre
Requires:      php-spl
Requires:      php-xmlreader
Requires:      php-xmlwriter

Obsoletes:     %{name}-test

Provides:      php-composer(nikic/php-parser) = %{version}


%description
A PHP parser written in PHP to simplify static analysis and code manipulation.


%prep
%setup -q -n %{github_name}-%{github_commit}


%build
# Empty build section, nothing to build


%install
mkdir -p -m 755 %{buildroot}%{_datadir}/php
cp -rp lib/%{lib_name} %{buildroot}%{_datadir}/php/

# Compat with old version (< 1.0.0)
mkdir -p -m 755 %{buildroot}%{_datadir}/php/%{lib_name_old}
ln -s ../%{lib_name}/Autoloader.php \
    %{buildroot}%{_datadir}/php/%{lib_name_old}/Autoloader.php


%check
%{_bindir}/phpunit


%files
%defattr(-,root,root,-)
%{!?_licensedir:%global license %%doc}
%license LICENSE
%doc *.md doc grammar composer.json
%{_datadir}/php/%{lib_name_old}
%{_datadir}/php/%{lib_name}


%changelog
* Wed Nov  5 2014 Remi Collet <remi@fedoraproject.org> 1.0.2-1
- Update to 1.0.2

* Thu Oct 16 2014 Remi Collet <remi@fedoraproject.org> 1.0.1-1
- Update to 1.0.1

* Fri Sep 12 2014 Remi Collet <remi@fedoraproject.org> 1.0.0-1
- Update to 1.0.0

* Wed Jul 23 2014 Remi Collet <remi@fedoraproject.org> 1.0.0-0.2.beta1
- composer dependencies
- fix license handling

* Mon May 12 2014 Remi Collet <remi@fedoraproject.org> 1.0.0-0.1.beta1
- Update to 1.0.0beta1
- library in /usr/share/php/PhpParser
- provide /usr/share/php/PHPParser/Autoloader.php for compatibility
- drop dependencies on xmlreader and xmlwriter

* Sat Nov 16 2013 Remi Collet <remi@fedoraproject.org> 0.9.4-1
- backport 0.9.4 for remi repo.

* Fri Nov 15 2013 Shawn Iwinski <shawn.iwinski@gmail.com> 0.9.4-1
- Updated to 0.9.4
- Spec cleanup

* Tue Jan  8 2013 Remi Collet <remi@fedoraproject.org> 0.9.3-2
- backport 0.9.3 for remi repo.

* Mon Dec 31 2012 Shawn Iwinski <shawn.iwinski@gmail.com> 0.9.3-2
- Added php_min_ver
- Fixed requires for php_min_ver and non-Fedora

* Thu Dec 20 2012 Shawn Iwinski <shawn.iwinski@gmail.com> 0.9.3-1
- Initial package
