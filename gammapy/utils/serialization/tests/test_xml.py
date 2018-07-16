# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import absolute_import, division, print_function, unicode_literals
import pytest
from ...testing import requires_data, requires_dependency
from ....cube import SourceLibrary
from ....spectrum import models as spectral
from ....image import models as spatial
from ...serialization import xml_to_source_library, UnknownModelError


@requires_data('gammapy-extra')
@requires_dependency('scipy')
def test_complex():
    filename = '$GAMMAPY_EXTRA/test_datasets/models/examples.xml'
    sourcelib = SourceLibrary.read(filename)

    assert len(sourcelib.skymodels) == 7

    model0 = sourcelib.skymodels[0]
    assert isinstance(model0.spectral_model, spectral.PowerLaw)
    assert isinstance(model0.spatial_model, spatial.SkyPointSource)

    model1 = sourcelib.skymodels[1]
    assert isinstance(model1.spectral_model, spectral.PowerLaw)
    assert isinstance(model1.spatial_model, spatial.SkyPointSource)

    pars1 = model1.parameters
    assert pars1['index'].value == 2.1
    assert pars1['index'].unit == ''
    assert pars1['index'].parmax == 1.0
    assert pars1['index'].parmin == 5.0
    assert pars1['index'].frozen == False

    assert pars1['lon_0'].value == 0.5
    assert pars1['lon_0'].unit == 'deg'
    assert pars1['lon_0'].parmax == 360
    assert pars1['lon_0'].parmin == -360
    assert pars1['lon_0'].frozen == True

    assert pars1['lat_0'].value == 1.0
    assert pars1['lat_0'].unit == 'deg'
    assert pars1['lat_0'].parmax == 90
    assert pars1['lat_0'].parmin == -90
    assert pars1['lat_0'].frozen == True

    model2 = sourcelib.skymodels[2]
    assert isinstance(model2.spectral_model, spectral.ExponentialCutoffPowerLaw)
    assert isinstance(model2.spatial_model, spatial.SkyGaussian)

    pars2 = model2.parameters
    assert pars2['sigma'].unit == 'deg'
    assert pars2['lambda_'].value == 0.01
    assert pars2['lambda_'].unit == 'MeV-1'
    assert pars2['lambda_'].parmin == 100
    assert pars2['lambda_'].parmax == 0.001
    assert pars2['index'].value == 2.2
    assert pars2['index'].unit == ''
    assert pars2['index'].parmax == 1.0
    assert pars2['index'].parmin == 5.0

    model3 = sourcelib.skymodels[3]
    assert isinstance(model3.spatial_model, spatial.SkyDisk)
    pars3 = model3.parameters
    assert pars3['r_0'].unit == 'deg'

    model4 = sourcelib.skymodels[4]
    assert isinstance(model4.spatial_model, spatial.SkyShell)
    pars4 = model4.parameters
    assert pars4['radius'].unit == 'deg'
    assert pars4['width'].unit == 'deg'

    model5 = sourcelib.skymodels[5]
    assert isinstance(model5.spatial_model, spatial.SkyDiffuseMap)

    model6 = sourcelib.skymodels[6]
    assert isinstance(model6.spatial_model, spatial.SkyDiffuseMap)


@pytest.mark.xfail(reason='Need to update model regsitry')
@requires_data('gammapy-extra')
@requires_dependency('scipy')
@pytest.mark.parametrize('filenames', [[
    '$GAMMAPY_EXTRA/test_datasets/models/fermi_model.xml',
    '$GAMMAPY_EXTRA/test_datasets/models/shell.xml',
]])
def test_models(filenames, tmpdir):
    outfile = tmpdir / 'models_out.xml'
    for filename in filenames:
        sourcelib = SourceLibrary.read(filename)
        sourcelib.to_xml(outfile)

        sourcelib_roundtrip = SourceLibrary.from_xml(outfile)

        for model, model_roundtrip in zip(sourcelib.skymodels,
                                          sourcelib_roundtrip.skymodels):
            assert str(model) == str(model_roundtrip)


def test_xml_errors():
    xml = '<?xml version="1.0" standalone="no"?>\n'
    xml += '<source_library title="broken source library">\n'
    xml += '    <source name="CrabShell" type="ExtendedSource">\n'
    xml += '        <spatialModel type="ElefantShapedSource">\n'
    xml += '            <parameter name="RA" value="1" scale="1" min="1" max="1" free="1"/>\n'
    xml += '        </spatialModel>\n'
    xml += '    </source>\n'
    xml += '</source_library>'

    with pytest.raises(UnknownModelError):
        xml_to_source_library(xml)

    # TODO: Think about a more elaborate XML validation scheme
