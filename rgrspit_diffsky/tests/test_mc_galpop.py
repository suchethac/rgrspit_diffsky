""" """

import numpy as np
from dsps.cosmology.defaults import DEFAULT_COSMOLOGY
from jax import random as jran

from .. import mc_galpop


def test_mc_subhalo_mass():
    """Enforce that mc_subhalo_mass generates subs with 10**lgmp_min<=Msub<=Mhost"""
    ran_key = jran.key(0)
    lgmp_min = 11.0
    n_halos = 500
    logmh_host = np.linspace(lgmp_min, 15, n_halos)
    subhalo_logmh, subs_host_halo_indx = mc_galpop._mc_subhalo_mass(
        ran_key, logmh_host, lgmp_min
    )
    assert np.all(np.isfinite(subhalo_logmh))
    assert np.all(subhalo_logmh >= lgmp_min)
    assert np.all(subs_host_halo_indx >= 0)
    assert np.all(subs_host_halo_indx < n_halos)

    subhalo_logmhost = logmh_host[subs_host_halo_indx]
    assert np.all(subhalo_logmhost >= subhalo_logmh)


def test_mc_diffmah_params_cens():
    ran_key = jran.key(0)
    lgmp_min = 11.0
    n_halos = 500
    logmh_host = np.linspace(lgmp_min, 15, n_halos)
    z_obs = 0.5
    mah_params = mc_galpop._mc_diffmah_params_cens(
        ran_key, logmh_host, z_obs, DEFAULT_COSMOLOGY
    )
    assert np.all(np.isfinite(mah_params))


def test_mc_diffmah_params_sats():
    ran_key = jran.key(0)
    lgmp_min = 11.0
    n_halos = 500
    logmh_host = np.linspace(lgmp_min, 15, n_halos)
    z_obs = 0.5
    mah_params = mc_galpop._mc_diffmah_params_sats(
        ran_key, logmh_host, z_obs, DEFAULT_COSMOLOGY
    )
    assert np.all(np.isfinite(mah_params))


def test_mc_diffmah_params_halopop_synthetic_subs():
    ran_key = jran.key(0)
    lgmp_min = 11.0
    n_halos = 500
    logmhost_at_z_obs = np.linspace(lgmp_min, 15, n_halos)
    z_obs = 0.5
    _res = mc_galpop._mc_diffmah_params_halopop_synthetic_subs(
        ran_key, logmhost_at_z_obs, z_obs, lgmp_min, DEFAULT_COSMOLOGY
    )
    mah_params_cens, mah_params_sats, subs_host_halo_indx, subs_mhalo_at_z_obs = _res
    assert np.all(np.isfinite(mah_params_cens))
    assert np.all(np.isfinite(mah_params_sats))
    assert np.all(np.isfinite(subs_host_halo_indx))
    assert np.all(np.isfinite(subs_mhalo_at_z_obs))


def test_mc_galpop_synthetic_subs():
    ran_key = jran.key(0)
    lgmp_min = 11.0
    n_halos = 500
    logmhost = np.linspace(lgmp_min, 15, n_halos)
    halo_radius = np.ones_like(logmhost)
    z_obs = 0.5
    mc_key, pos_key, vel_key = jran.split(ran_key, 3)
    halo_pos = jran.uniform(pos_key, shape=(n_halos, 3))
    halo_vel = jran.uniform(vel_key, shape=(n_halos, 3))
    Lbox = 2_000.0

    galcat = mc_galpop.mc_galpop_synthetic_subs(
        mc_key,
        logmhost,
        halo_radius,
        halo_pos,
        halo_vel,
        z_obs,
        lgmp_min,
        DEFAULT_COSMOLOGY,
        Lbox,
    )
    for key, val in galcat.items():
        if key == "sfh_params":
            assert np.all(np.isfinite(val.ms_params)), key
            assert np.all(np.isfinite(val.q_params)), key
        else:
            assert np.all(np.isfinite(val)), key

    assert np.all(galcat["pos"] >= 0)
    assert np.all(galcat["pos"] <= Lbox)
