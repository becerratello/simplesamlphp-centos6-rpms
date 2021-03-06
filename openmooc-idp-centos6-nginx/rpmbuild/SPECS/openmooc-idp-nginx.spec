%global ssp simplesamlphp
%global theme_module sspopenmooc
%global ldap_scheme_path /etc/openldap/schema
%global crond_path /etc/cron.d

Name: openmooc-idp-nginx
Version: 0.1.1
Release: 4%{?dist}
Summary: OpenMOOC IdP: simplesamlphp + userregistration + sspopenmooc

#TODO: Improve nginx to serve phpldapadmin directly and avoid the use of a symbolic link

Group: Applications/Internet
License: LGPLv2
URL: https://github.com/OpenMOOC/sspopenmooc/
# OpenMOOC theme for SimpleSAMLphp
Source0: https://github.com/OpenMOOC/sspopenmooc/archive/sspopenmooc-v%{version}.tar.gz
# LDAP schemas
Source1: openmooc-idp-ldap-schemas-v%{version}.tar.gz
# SimpleSAMLphp configs
Source2: config-metarefresh.php
Source3: config-sanitycheck.php
Source4: extended_config.php
Source5: module_cron.php
Source6: openmooc_components.php
# IdP Metadata
Source7: saml20-idp-hosted.php
Source12: openmooc-metarefresh
# Nginx // php-fpm settings
Source8: idp.conf
Source9: htpasswd
Source10: idp-fpm.conf

#sspopenmooc
Source11: module_sspopenmooc.php

BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

%global theme_source sspopenmooc-v%{version}
%global schema_source openmooc-idp-ldap-schemas-v%{version}

%if 0%{?el6}
Requires: simplesamlphp
Requires: nginx
Requires: php-fpm
Requires: mod_ssl
Requires: php-mcrypt
Requires: php-mbstring
Requires: zlib
Requires: wget
Requires: ntp
Requires: simplesamlphp-userregistration
# simplesamlphp-userregistration dependences for OpenMOOC
Requires: php-pecl-mongo
Requires: mongo-10gen-server
Requires: postfix

%endif 

BuildArch: noarch
 
%description
The IdP (Identity Provider) is one of the OpenMOOC platform components.
Is based on SimpleSAMLphp and some extra modules, incluiding a default
openmooc theme.

%prep
%setup -q -b 0 -n %theme_source
%setup -q -b 1 -n %schema_source -c

%build

%install

mkdir -p ${RPM_BUILD_ROOT}%{_libdir}/%{ssp}/modules/%{theme_module}
cp -pr %theme_source/* ${RPM_BUILD_ROOT}%{_libdir}/%{ssp}/modules/%{theme_module}

mkdir -p ${RPM_BUILD_ROOT}%{_libdir}/%{ssp}/modules/metarefresh
mkdir -p ${RPM_BUILD_ROOT}%{_libdir}/%{ssp}/modules/cron/
touch ${RPM_BUILD_ROOT}%{_libdir}/%{ssp}/modules/metarefresh/enable
touch ${RPM_BUILD_ROOT}%{_libdir}/%{ssp}/modules/cron/enable

mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/lib/%{ssp}/metadata/moocng
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/lib/%{ssp}/metadata/askbot

mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/%{ssp}/config/

cp %{SOURCE2} ${RPM_BUILD_ROOT}%{_sysconfdir}/%{ssp}/config/config-metarefresh.php
cp %{SOURCE3} ${RPM_BUILD_ROOT}%{_sysconfdir}/%{ssp}/config/config-sanitycheck.php
cp %{SOURCE4} ${RPM_BUILD_ROOT}%{_sysconfdir}/%{ssp}/config/extended_config.php
cp %{SOURCE5} ${RPM_BUILD_ROOT}%{_sysconfdir}/%{ssp}/config/module_cron.php
cp %{SOURCE6} ${RPM_BUILD_ROOT}%{_sysconfdir}/%{ssp}/config/openmooc_components.php

cp %{SOURCE7} ${RPM_BUILD_ROOT}%{_localstatedir}/lib/%{ssp}/metadata/saml20-idp-hosted.php

cp %{SOURCE11} ${RPM_BUILD_ROOT}%{_sysconfdir}/%{ssp}/config/module_sspopenmooc.php

# Copy ldap schemas
mkdir -p ${RPM_BUILD_ROOT}%{ldap_scheme_path}
cp %schema_source/eduperson.schema ${RPM_BUILD_ROOT}%{ldap_scheme_path}/eduperson.schema
cp %schema_source/iris.schema ${RPM_BUILD_ROOT}%{ldap_scheme_path}/iris.schema
cp %schema_source/schac.schema ${RPM_BUILD_ROOT}%{ldap_scheme_path}/schac.schema

# nginx
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/nginx/conf.d/
cp %{SOURCE8} $RPM_BUILD_ROOT%{_sysconfdir}/nginx/conf.d/idp.conf
cp %{SOURCE9} $RPM_BUILD_ROOT%{_sysconfdir}/nginx/htpasswd

# php-fpm
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/php-fpm.d/
cp %{SOURCE10} $RPM_BUILD_ROOT%{_sysconfdir}/php-fpm.d/idp-fpm.conf

# nginx's session
mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/lib/%{ssp}/data/session

# crond metarefresh
mkdir -p ${RPM_BUILD_ROOT}%{crond_path}
cp %{SOURCE12} ${RPM_BUILD_ROOT}%{crond_path}/

%clean
rm -rf ${RPM_BUILD_ROOT}


%pre
/usr/bin/gpasswd -a nginx %{ssp}


%post
sed "s/@SERVER_NAME@/${HOSTNAME:-localhost}/g" -i %{_sysconfdir}/nginx/conf.d/idp.conf

# Ignore default php-fpm configuration file
[ -f %{_sysconfdir}/php-fpm.d/www.conf ] && mv %{_sysconfdir}/php-fpm.d/www.conf %{_sysconfdir}/php-fpm.d/www.conf.default

# phpldapadmin, override the apache perm
chown -R :%{ssp} %{_sysconfdir}/phpldapadmin
chown -R :%{ssp} %{_datadir}/phpldapadmin

# link phpldapadmin in simplesamlphp folder
[ ! -d %{_libdir}/%{ssp}/www/phpldapadmin ] && ln -s %{_datadir}/phpldapadmin %{_libdir}/%{ssp}/www/phpldapadmin

# session folder permission
chmod +s %{_localstatedir}/lib/%{ssp}/data/session

%files
%defattr(644,root,root,755)

%attr(640,root,simplesamlphp) %config(noreplace) %{_sysconfdir}/%{ssp}/config/module_sspopenmooc.php
%attr(640,root,simplesamlphp) %config(noreplace) %{_sysconfdir}/%{ssp}/config/extended_config.php
%attr(640,root,simplesamlphp) %config(noreplace) %{_sysconfdir}/%{ssp}/config/config-metarefresh.php
%attr(640,root,simplesamlphp) %config(noreplace) %{_sysconfdir}/%{ssp}/config/config-sanitycheck.php
%attr(640,root,simplesamlphp) %config(noreplace) %{_sysconfdir}/%{ssp}/config/module_cron.php
%attr(640,root,simplesamlphp) %config(noreplace) %{_sysconfdir}/%{ssp}/config/openmooc_components.php

%attr(640,root,simplesamlphp) %config(noreplace) %{_localstatedir}/lib/%{ssp}/metadata/saml20-idp-hosted.php

%attr(770,root,simplesamlphp) %{_localstatedir}/lib/%{ssp}/metadata/moocng
%attr(770,root,simplesamlphp) %{_localstatedir}/lib/%{ssp}/metadata/askbot

# nginx
%attr(644,root,simplesamlphp) %config(noreplace) %{_sysconfdir}/nginx/conf.d/idp.conf
%attr(644,root,simplesamlphp) %config(noreplace) %{_sysconfdir}/nginx/htpasswd

# php-fpm
%attr(644,root,simplesamlphp) %config(noreplace) %{_sysconfdir}/php-fpm.d/idp-fpm.conf

%attr(770,root,simplesamlphp) %{_localstatedir}/lib/%{ssp}/data/session

%attr(640,root,simplesamlphp) %{_libdir}/%{ssp}/modules/cron/enable
%attr(640,root,simplesamlphp) %{_libdir}/%{ssp}/modules/metarefresh/enable

%{_libdir}/%{ssp}/modules/%{theme_module}

%{ldap_scheme_path}/eduperson.schema
%{ldap_scheme_path}/iris.schema
%{ldap_scheme_path}/schac.schema

# crond metarefresh
%attr(644,root,simplesamlphp) %{crond_path}/openmooc-metarefresh

%changelog
* Mon Jul 10 2013 <smartin@yaco.es> - 0.1.0-1
- initial package
