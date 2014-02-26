%{!?__pear:       %global __pear %{_bindir}/pear}
%global pear_name Crypt_DES

Name:           php-phpseclib-crypt-des
Version:        0.3.6
Release:        1%{?dist}
Summary:        Pure-PHP implementation of DES

Group:          Development/Libraries
License:        MIT
URL:            http://phpseclib.sourceforge.net/
Source0:        http://phpseclib.sourceforge.net/get/%{pear_name}-%{version}.tgz

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  php-pear(PEAR)

Requires(post): %{__pear}
Requires(postun): %{__pear}
Requires:       php-pear(PEAR)
Provides:       php-pear(phpseclib.sourceforge.net/Crypt_DES) = %{version}
BuildRequires:  php-channel(phpseclib.sourceforge.net)
Requires:       php-channel(phpseclib.sourceforge.net)
Requires:       php-pear(phpseclib.sourceforge.net/Crypt_Hash)

%description
Uses mcrypt, if available, and an internal implementation, otherwise.

%prep
%setup -q -c
mv package.xml %{pear_name}-%{version}/%{name}.xml

cd %{pear_name}-%{version}


%build
cd %{pear_name}-%{version}
# Empty build section, most likely nothing required.


%install
rm -rf %{buildroot}
cd %{pear_name}-%{version}
%{__pear} install --nodeps --packagingroot %{buildroot} %{name}.xml

# Clean up unnecessary files
rm -rf %{buildroot}%{pear_metadir}/.??*

# Install XML package description
mkdir -p %{buildroot}%{pear_xmldir}
install -pm 644 %{name}.xml %{buildroot}%{pear_xmldir}


%clean
rm -rf %{buildroot}


%post
%{__pear} install --nodeps --soft --force --register-only \
    %{pear_xmldir}/%{name}.xml >/dev/null || :

%postun
if [ $1 -eq 0 ] ; then
    %{__pear} uninstall --nodeps --ignore-errors --register-only \
        phpseclib.sourceforge.net/%{pear_name} >/dev/null || :
fi


%files
%defattr(-, root, root, -)
%{pear_xmldir}/%{name}.xml
%{pear_phpdir}/Crypt/DES.php


%changelog
* Wed Feb 26 2014 Remi Collet <remi@fedoraproject.org> - 0.3.6-1
- Update to 0.3.6

* Wed Jan 15 2014 Remi Collet <rpms@famillecollet.com> - 0.3.5-3
- backport for remi repo

* Thu Jan 09 2014 Adam Williamson <awilliam@redhat.com> - 0.3.5-3
- requires crypt-hash, drop ownership of Crypt dir

* Sat Jan  4 2014 Adam Williamson <awilliam@redhat.com> - 0.3.5-2
- various review style cleanups

* Tue Dec 31 2013 Adam Williamson <awilliam@redhat.com> - 0.3.5-1
- initial package (generated with pear make-rpm-spec)
