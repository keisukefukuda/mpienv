# coding: utf-8

import unittest

import ompi


Text = """
package:Open MPI keisukefukuda@KeisukenoMacBook-Pro.local Distribution
ompi:version:full:2.1.1
ompi:version:repo:v2.1.0-100-ga2fdb5b
ompi:version:release_date:May 10, 2017
orte:version:full:2.1.1
orte:version:repo:v2.1.0-100-ga2fdb5b
orte:version:release_date:May 10, 2017
opal:version:full:2.1.1
opal:version:repo:v2.1.0-100-ga2fdb5b
opal:version:release_date:May 10, 2017
mpi-api:version:full:3.1.0
ident:2.1.1
path:prefix:/Users/keisukefukuda/mpi/openmpi-2.1.1
path:exec_prefix:/Users/keisukefukuda/mpi/openmpi-2.1.1
path:bindir:/Users/keisukefukuda/mpi/openmpi-2.1.1/bin
path:sbindir:/Users/keisukefukuda/mpi/openmpi-2.1.1/sbin
path:libdir:/Users/keisukefukuda/mpi/openmpi-2.1.1/lib
path:incdir:/Users/keisukefukuda/mpi/openmpi-2.1.1/include
path:mandir:/Users/keisukefukuda/mpi/openmpi-2.1.1/share/man
path:pkglibdir:/Users/keisukefukuda/mpi/openmpi-2.1.1/lib/openmpi
path:libexecdir:/Users/keisukefukuda/mpi/openmpi-2.1.1/libexec
path:datarootdir:/Users/keisukefukuda/mpi/openmpi-2.1.1/share
path:datadir:/Users/keisukefukuda/mpi/openmpi-2.1.1/share
path:sysconfdir:/Users/keisukefukuda/mpi/openmpi-2.1.1/etc
path:sharedstatedir:/Users/keisukefukuda/mpi/openmpi-2.1.1/com
path:localstatedir:/Users/keisukefukuda/mpi/openmpi-2.1.1/var
path:infodir:/Users/keisukefukuda/mpi/openmpi-2.1.1/share/info
path:pkgdatadir:/Users/keisukefukuda/mpi/openmpi-2.1.1/share/openmpi
path:pkglibdir:/Users/keisukefukuda/mpi/openmpi-2.1.1/lib/openmpi
path:pkgincludedir:/Users/keisukefukuda/mpi/openmpi-2.1.1/include/openmpi
compiler:fortran:value:true:77
mca:mca:base:param:mca_param_files:value:"/Users/keisukefukuda/.openmpi/mca-params.conf:/Users/keisukefukuda/mpi/openmpi-2.1.1/etc/openmpi-mca-params.conf"
mca:mca:base:param:mca_component_path:value:"/Users/keisukefukuda/mpi/openmpi-2.1.1/lib/openmpi:/Users/keisukefukuda/.openmpi/components"
mca:mca:base:param:mca_component_show_load_errors:value:true
mca:mca:base:param:mca_component_show_load_errors:enumerator:value:0:false

"""


class TestOmpi(unittest.TestCase):
    def test_ompi_info(self):
        info = ompi.parse_ompi_info(Text)
        self.assertEqual("2.1.1", info.get('ident'))
        self.assertEqual("2.1.1", info.get('ompi:version:full'))
        self.assertEqual("77", info.get('compiler:fortran:value:true'))
