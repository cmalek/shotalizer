%{!?tgrelease: %define tgrelease() %2}
%define __python python
%define __python_ver python2.6
%define __python_prefix python
%define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")

%define __package shotalizer
%define __package_safe %(echo %{__package} | sed 's/[-. ]/_/g')
%define __pip_package %(echo %{__package} | sed 's/_/-/g' | tr '[A-Z]' '[a-z]')

%define __requirements requirements.txt

Name:           %{__package}
Version:        %{__version}
Release:        %tgrelease 0 1
Summary:        Generate random crops from a set of images
Group:          Development/Languages
License:        Restricted
Source0:        %{rname}/%{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  %{__python_prefix}
BuildRequires:  %{__python_prefix}-setuptools
BuildRequires:  %{__python_prefix}-virtualenv
%if 0%{?amzn:1}
# Include git in the general case when we have git installed from RPM on RH6
BuildRequires:  git
BuildRequires:  chrpath
%endif

Requires:  %{__python_prefix}
Requires:  %{__python_prefix}-virtualenv

%description
Generate random crops from a set of images

%prep
%setup -q -n %{name}-%{version}

%install
rm -rf $RPM_BUILD_ROOT

#virtualenv
virtualenv-2.6 --no-site-packages %{buildroot}/srv/ads/python/ve/%{name}
source  %{buildroot}/srv/ads/python/ve/%{name}/bin/activate
pip install -r %{__requirements}
virtualenv-2.6 --relocatable %{buildroot}/srv/ads/python/ve/%{name}
deactivate

#fix the wrong paths in easy_install.pth
perl -p -i -e "s#$RPM_BUILD_ROOT##g" %{buildroot}/srv/ads/python/ve/%{name}/lib/%{__python_ver}/site-packages/easy-install.pth
#fix the wrong paths in activate
perl -p -i -e "s#$RPM_BUILD_ROOT##g" %{buildroot}/srv/ads/python/ve/%{name}/bin/activate*

# Un prelink everything
# http://www.alexhudson.com/2013/05/24/packaging-a-virtualenv-really-not-relocatable/
find %{buildroot}/srv/ads/python/ve/%{name} -type f -perm /u+x,g+x -exec /usr/sbin/prelink -u {} \;
# re-point the lib64 symlink - not needed on newer virtualenv
if test -d %{buildroot}/srv/ads/python/ve/%{name}/lib64; then
  rm %{buildroot}/srv/ads/python/ve/%{name}/lib64
  ln -sf /srv/ads/python/ve/%{name}/lib %{buildroot}/srv/ads/python/ve/%{name}/lib64
fi

%if 0%{?amzn:1}
# The latest Amazon Linux 64bit rpm-build environment is more persnickety about 
# rpaths in libraries pointing to directories that don't exist.  So we use
# chrpath to purge them.
chrpath --delete %{buildroot}/srv/ads/python/ve/%{name}/lib/python2.6/site-packages/_ldap.so
%endif

#symlinks
pushd %{buildroot}/srv/ads/python
cd bin
ln -s ../ve/%{name}/src/%{__pip_package}/bin %{name}


%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
/srv/ads/python/bin/*
/srv/ads/python/ve/%{name}/*


