"""Plotting utilities for the official basic AI Economist example.

Copyright (c) 2020, salesforce.com, inc.
SPDX-License-Identifier: BSD-3-Clause
Source: https://github.com/salesforce/ai-economist/blob/master/tutorials/utils/plotting.py

Only compatibility-level edits were made for use as a regular Python module.
"""

import matplotlib.pyplot as plt
import numpy as np
from ai_economist.foundation import landmarks, resources


def plot_map(maps, locs, ax=None, cmap_order=None):
    world_size = np.array(maps.get("Wood")).shape
    max_health = {"Wood": 1, "Stone": 1, "House": 1}
    n_agents = len(locs)

    if ax is None:
        _, ax = plt.subplots(1, 1, figsize=(10, 10))
    else:
        ax.cla()
    image = np.zeros((3, world_size[0], world_size[1]))
    cmap = plt.get_cmap("jet", n_agents)
    cmap_order = list(range(n_agents)) if cmap_order is None else list(cmap_order)
    assert len(cmap_order) == n_agents

    scenario_entities = [key for key in maps.keys() if "source" not in key.lower()]
    for entity in scenario_entities:
        if entity == "House":
            continue
        if resources.has(entity) and resources.get(entity).collectible:
            entity_map = (
                resources.get(entity).color[:, None, None]
                * np.array(maps.get(entity))[None]
            )
            image += entity_map / max_health[entity]
        elif landmarks.has(entity):
            image += (
                landmarks.get(entity).color[:, None, None]
                * np.array(maps.get(entity))[None]
            )

    if isinstance(maps, dict):
        house_idx = np.array(maps.get("House")["owner"])
        house_health = np.array(maps.get("House")["health"])
    else:
        house_idx = maps.get("House", owner=True)
        house_health = maps.get("House")

    for index in range(n_agents):
        houses = house_health * (house_idx == cmap_order[index])
        color = np.array(cmap(index)[:3])
        image += color[:, None, None] * houses[None]

    image = np.minimum(np.transpose(image * 0.7 + 0.3, [1, 2, 0]), 1.0)
    ax.imshow(image, vmax=1.0, aspect="auto")
    bbox = ax.get_window_extent()

    for index in range(n_agents):
        row, column = locs[cmap_order[index]]
        color = np.array(cmap(index)[:3])
        ax.plot(column, row, "o", markersize=bbox.height * 20 / 550, color="w")
        ax.plot(column, row, "*", markersize=bbox.height * 15 / 550, color=color)

    ax.set_xticks([])
    ax.set_yticks([])


def plot_env_state(env, ax=None, remap_key=None):
    maps = env.world.maps
    locs = [agent.loc for agent in env.world.agents]
    if remap_key is None:
        cmap_order = None
    else:
        cmap_order = np.argsort(
            [agent.state[remap_key] for agent in env.world.agents]
        ).tolist()
    plot_map(maps, locs, ax, cmap_order)


def plot_log_state(dense_log, timestep, ax=None, remap_key=None):
    maps = dense_log["world"][timestep]
    states = dense_log["states"][timestep]
    n_agents = len(states) - 1
    locs = [states[str(index)]["loc"] for index in range(n_agents)]
    if remap_key is None:
        cmap_order = None
    else:
        key_values = np.array(
            [dense_log["states"][0][str(index)][remap_key] for index in range(n_agents)]
        )
        cmap_order = np.argsort(key_values).tolist()
    plot_map(maps, locs, ax, cmap_order)


def _format_logs_and_eps(dense_logs, eps):
    if isinstance(dense_logs, dict):
        return [dense_logs], [0]
    assert isinstance(dense_logs, (list, tuple))
    if isinstance(eps, (list, tuple)):
        return dense_logs, list(eps)
    if isinstance(eps, (int, float)):
        return dense_logs, [int(eps)]
    if eps is None:
        return dense_logs, list(range(np.minimum(len(dense_logs), 16)))
    raise NotImplementedError


def vis_world_array(dense_logs, timesteps, eps=None, axes=None, remap_key=None):
    dense_logs, eps = _format_logs_and_eps(dense_logs, eps)
    if isinstance(timesteps, (int, float)):
        timesteps = [timesteps]

    if axes is None:
        fig, axes = plt.subplots(
            len(eps),
            len(timesteps),
            figsize=(np.minimum(3.2 * len(timesteps), 16), 3 * len(eps)),
            squeeze=False,
        )
    else:
        fig = None
        if len(timesteps) == 1 and len(eps) == 1:
            axes = np.array([[axes]]).reshape(1, 1)
        else:
            axes = np.array(axes).reshape(len(eps), len(timesteps))

    for timestep_index, timestep in enumerate(timesteps):
        for episode_index, episode in enumerate(eps):
            plot_log_state(
                dense_logs[episode],
                timestep,
                ax=axes[episode_index, timestep_index],
                remap_key=remap_key,
            )

    for ax, timestep in zip(axes[0], timesteps):
        ax.set_title(f"T = {timestep}")
    for ax, episode in zip(axes[:, 0], eps):
        ax.set_ylabel(f"Episode {episode}")
    return fig


def vis_world_range(
    dense_logs, t0=0, tN=None, N=5, eps=None, axes=None, remap_key=None
):
    dense_logs, eps = _format_logs_and_eps(dense_logs, eps)
    viable_timesteps = np.array(
        [index for index, world in enumerate(dense_logs[0]["world"]) if world]
    )
    if tN is None:
        tN = viable_timesteps[-1]
    assert 0 <= t0 < tN
    target_timesteps = np.linspace(t0, tN, N).astype(int)

    timesteps = set()
    for target in target_timesteps:
        closest = np.argmin(np.abs(target - viable_timesteps))
        timesteps.add(viable_timesteps[closest])
    timesteps = sorted(timesteps)
    if axes is not None:
        axes = axes[: len(timesteps)]
    return vis_world_array(
        dense_logs, timesteps, axes=axes, eps=eps, remap_key=remap_key
    )


def _trade_str(trades, resource, agent, income=True):
    field = "income" if income else "cost"
    role = "seller" if income else "buyer"
    values = [item[field] for item in trades[resource] if item[role] == agent]
    if values:
        return f"{np.mean(values):6.2f} (n={len(values):3d})"
    return "   ~~~~~~~~   "


def _full_trade_str(trades, resource, agent_indices, income=True):
    head = "{} ({})".format("Income" if income else "Cost", resource)
    values = [_trade_str(trades, resource, agent, income) for agent in agent_indices]
    return "{:<15}: {}".format(head, " | ".join(values))


def _build_str(builds, agent):
    values = [item["income"] for item in builds if item["builder"] == agent]
    if values:
        return f"{np.mean(values):6.2f} (n={len(values):3d})"
    return "   ~~~~~~~~   "


def _report(trades, builds, n_agents, agent_indices):
    head = ("_" * 15) + ":_"
    tail = "_|_".join([f" Agent {i:2d} ____" for i in range(n_agents)])
    print(head + tail)
    if trades is not None:
        for resource in ["Wood", "Stone"]:
            print(_full_trade_str(trades, resource, agent_indices, income=False))
        print("")
        for resource in ["Wood", "Stone"]:
            print(_full_trade_str(trades, resource, agent_indices, income=True))
    build_values = [_build_str(builds, builder) for builder in agent_indices]
    print("{:<15}: {}".format("Income (Build)", " | ".join(build_values)))


def breakdown(log, remap_key=None):
    """Create the same summary figures and report as the official tutorial."""
    fig0 = vis_world_range(log, remap_key=remap_key)
    n_agents = len(list(log["states"][0].keys())) - 1
    trading_active = "Trade" in log
    if remap_key is None:
        agent_indices = list(range(n_agents))
    else:
        key_values = np.array(
            [log["states"][0][str(index)][remap_key] for index in range(n_agents)]
        )
        agent_indices = np.argsort(key_values).tolist()

    all_builds = []
    for timestep, builds in enumerate(log["Build"]):
        entries = builds["builds"] if isinstance(builds, dict) else builds
        for build in entries:
            all_builds.append({"t": timestep, **build})

    trades_by_resource = None
    if trading_active:
        trades_by_resource = {"Stone": [], "Wood": []}
        for timestep, trades in enumerate(log["Trade"]):
            entries = trades["trades"] if isinstance(trades, dict) else trades
            for trade in entries:
                item = {
                    "t": timestep,
                    "t_ask": timestep - trade["ask_lifetime"],
                    "t_bid": timestep - trade["bid_lifetime"],
                    **trade,
                }
                trades_by_resource[trade["commodity"]].append(item)

    _report(trades_by_resource, all_builds, n_agents, agent_indices)
    cmap = plt.get_cmap("jet", n_agents)
    fig1, axes = plt.subplots(1, 4, figsize=(16, 4), sharey=False)
    for resource_name, ax in zip(["Wood", "Stone", "Coin"], axes):
        for index in range(n_agents):
            agent = str(agent_indices[index])
            ax.plot(
                [
                    state[agent]["inventory"][resource_name]
                    + state[agent]["escrow"][resource_name]
                    for state in log["states"]
                ],
                label=index,
                color=cmap(index),
            )
        ax.set_title(resource_name)
        ax.legend()
        ax.grid(True)

    for index in range(n_agents):
        agent = str(agent_indices[index])
        axes[-1].plot(
            [state[agent]["endogenous"]["Labor"] for state in log["states"]],
            label=index,
            color=cmap(index),
        )
    axes[-1].set_title("Labor")
    axes[-1].legend()
    axes[-1].grid(True)

    map_shape = np.array(log["world"][0]["Stone"]).shape
    n_small = np.minimum(4, n_agents)
    fig2, movement_axes = plt.subplots(
        2 if trading_active else 1,
        n_small,
        figsize=(16, 8 if trading_active else 4),
        sharex="row",
        sharey="row",
        squeeze=False,
    )
    for index, ax in enumerate(movement_axes[0]):
        agent = str(agent_indices[index])
        rows = np.array([state[agent]["loc"][0] for state in log["states"]]) * -1
        columns = np.array([state[agent]["loc"][1] for state in log["states"]])
        ax.plot(columns[::20], rows[::20])
        ax.plot(columns[0], rows[0], "r*", markersize=15)
        ax.plot(columns[-1], rows[-1], "g*", markersize=15)
        ax.set_title(f"Agent {index}")
        ax.set_xlim([-1, 1 + map_shape[1]])
        ax.set_ylim([-(1 + map_shape[0]), 1])

    if trading_active:
        for index, ax in enumerate(movement_axes[1]):
            for resource_name in ["Wood", "Stone"]:
                sells = [
                    (trade["t"], trade["income"])
                    for trade in trades_by_resource[resource_name]
                    if trade["seller"] == agent_indices[index]
                ]
                buys = [
                    (trade["t"], -trade["cost"])
                    for trade in trades_by_resource[resource_name]
                    if trade["buyer"] == agent_indices[index]
                ]
                for values in [sells, buys]:
                    if values:
                        timesteps, prices = [np.array(value) for value in zip(*values)]
                        color = resources.get(resource_name).color
                        ax.plot(
                            np.stack([timesteps, timesteps]),
                            np.stack([np.zeros_like(prices), prices]),
                            color=color,
                        )
                        ax.plot(timesteps, prices, ".", color=color, markersize=12)
            ax.set_xlim([-20, len(log["states"]) + 19])
            ax.grid(True)
            ax.set_facecolor([0.3, 0.3, 0.3])

    return fig0, fig1, fig2
