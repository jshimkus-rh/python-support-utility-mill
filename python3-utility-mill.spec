%global modname utility-mill

%define repo_name python-support-utility-mill
%define repo_branch main

%define version 1.0.6
%define unmangled_version 1.0.6
%define release 1

Name: python3-%{modname}
Version: %{version}
Release: %{release}
Summary: python3-%{modname}
License: BSD
URL:     https://github.com/dm-vdo/%{repo_name}
Source0: %{url}/archive/refs/heads/%{repo_branch}.tar.gz

BuildArch: noarch

Group: Development/Libraries

# Build requirements.
%if 0%{?rhel} && 0%{?rhel} < 9
BuildRequires: python39
BuildRequires: python39-devel
BuildRequires: python39-rpm-macros
BuildRequires: python39-setuptools
BuildRequires: python39-six
BuildRequires: python39-pyyaml
%else
BuildRequires: python3
BuildRequires: python3-devel
BuildRequires: python3-eventlet
BuildRequires: python3-py
BuildRequires: python3-rpm-macros
BuildRequires: python3-setuptools
BuildRequires: python3-six
BuildRequires: python3-pyyaml
%endif

# Runtime requirements.
%if 0%{?rhel} && 0%{?rhel} < 9
Requires: python39
Requires: python39-pyyaml
%else
Requires: python3
Requires: python3-pyyaml
%endif

%?python_enable_dependency_generator

%description
UNKNOWN

%prep
%autosetup -n %{repo_name}-%{repo_branch}

%build
%py3_build

%install
%py3_install

%files -n python3-%{modname}
%{python3_sitelib}/mill/
%{python3_sitelib}/python3_utility_mill-%{version}*

%changelog
* Mon Oct 24 2022 Joe Shimkus <jshimkus@redhat.com> - 1.0.6-1
- Changed package generation per Red Hat example.

* Tue Jul 26 2022 Joe Shimkus <jshimkus@redhat.com> - 1.0.5-1
- Make functional rpm for RHEL earlier than 9.0.
- Sync version with setup.py.
