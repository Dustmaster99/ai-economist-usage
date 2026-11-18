"""Versão Python do tutorial oficial ``economic_simulation_basic.ipynb``.

Fonte: https://github.com/salesforce/ai-economist/blob/master/tutorials/
       economic_simulation_basic.ipynb

Copyright (c) 2020, salesforce.com, inc.
SPDX-License-Identifier: BSD-3-Clause

As células específicas do Colab (clone, pip e reinício do kernel) foram removidas.
As expressões exibidas automaticamente pelo notebook são impressas explicitamente,
e as visualizações são abertas em janelas Matplotlib ao final da execução.
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
from ai_economist import foundation

from src.official_examples.economic_simulation_basic import plotting

ENV_CONFIG = {
    # ===== SCENARIO CLASS =====
    "scenario_name": "layout_from_file/simple_wood_and_stone",
    # ===== COMPONENTS =====
    "components": [
        ("Build", {"skill_dist": "pareto", "payment_max_skill_multiplier": 3}),
        ("ContinuousDoubleAuction", {"max_num_orders": 5}),
        ("Gather", {}),
    ],
    # ===== SCENARIO CLASS ARGUMENTS =====
    "env_layout_file": "quadrant_25x25_20each_30clump.txt",
    "starting_agent_coin": 10,
    "fixed_four_skill_and_loc": True,
    # ===== STANDARD ARGUMENTS =====
    "n_agents": 4,
    "world_size": [25, 25],
    "episode_length": 1000,
    "multi_action_mode_agents": False,
    "multi_action_mode_planner": True,
    "flatten_observations": False,
    "flatten_masks": True,
}


def sample_random_action(agent, mask):
    """Sample random unmasked action(s) for an agent."""
    if agent.multi_action_mode:
        split_masks = np.split(mask, agent.action_spaces.cumsum()[:-1])
        return [
            np.random.choice(np.arange(len(split_mask)), p=split_mask / split_mask.sum())
            for split_mask in split_masks
        ]
    return np.random.choice(np.arange(agent.action_spaces), p=mask / mask.sum())


def sample_random_actions(env, obs):
    """Sample random unmasked actions for every agent in an observation."""
    return {
        agent_idx: sample_random_action(env.get_agent(agent_idx), agent_obs["action_mask"])
        for agent_idx, agent_obs in obs.items()
    }


def do_plot(env, ax, fig):
    """Plot the current world state during episode sampling."""
    plotting.plot_env_state(env, ax)
    ax.set_aspect("equal")
    fig.canvas.draw_idle()
    plt.pause(0.001)


def play_random_episode(env, plot_every=100, do_dense_logging=False):
    """Play a complete episode using randomly sampled valid actions."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    obs = env.reset(force_dense_logging=do_dense_logging)

    for timestep in range(env.episode_length):
        actions = sample_random_actions(env, obs)
        obs, rew, done, info = env.step(actions)
        if ((timestep + 1) % plot_every) == 0:
            do_plot(env, ax, fig)

    if env.episode_length % plot_every != 0:
        do_plot(env, ax, fig)
    return fig


def _save_figure(fig, output_dir: Path, filename: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / filename, dpi=150, bbox_inches="tight")


def _print_episode_summary(dense_log) -> None:
    final_state = dense_log["states"][-1]
    print("\nFinal dense-logged episode state:")
    print("agent | coin | wood | stone | labor | builds")
    for agent_index in range(4):
        agent = final_state[str(agent_index)]
        totals = {
            resource: agent["inventory"][resource] + agent["escrow"][resource]
            for resource in ("Coin", "Wood", "Stone")
        }
        builds = sum(
            1
            for timestep_builds in dense_log["Build"]
            for build in (
                timestep_builds["builds"]
                if isinstance(timestep_builds, dict)
                else timestep_builds
            )
            if build["builder"] == agent_index
        )
        print(
            f"{agent_index:5d} | {totals['Coin']:4.0f} | {totals['Wood']:4.0f} | "
            f"{totals['Stone']:5.0f} | {agent['endogenous']['Labor']:5.1f} | {builds:6d}"
        )


def run(
    show_plots: bool = True,
    output_dir: Optional[Path] = None,
    seed: int = 42,
) -> None:
    """Execute the official basic economic simulation tutorial."""
    random.seed(seed)
    np.random.seed(seed)

    print("Creating the Foundation environment...")
    env = foundation.make_env_instance(**ENV_CONFIG)

    print("\nAgent 0:")
    print(env.get_agent(0))

    obs = env.reset()
    actions = sample_random_actions(env, obs)
    obs, rew, done, info = env.step(actions)

    print("\nObservation keys:")
    print(obs.keys())

    print("\nAgent 0 observation fields:")
    for key, value in obs["0"].items():
        print(f"{key:50} {type(value)}")

    print("\nRewards:")
    for agent_idx, reward in rew.items():
        print(f"{agent_idx:2} {reward:.3f}")

    print("\nDone:")
    print(done)
    print("\nInfo:")
    print(info)

    print("\nPlaying a random episode...")
    random_episode_fig = play_random_episode(env, plot_every=100)

    print("\nPlaying another episode with dense logging...")
    dense_episode_fig = play_random_episode(env, plot_every=100, do_dense_logging=True)
    dense_log = env.previous_episode_dense_log

    print("\nVisualizing world state from t=0 to t=200...")
    early_world_fig = plotting.vis_world_range(dense_log, t0=0, tN=200, N=5)

    print("Visualizing the complete episode...")
    complete_world_fig = plotting.vis_world_range(dense_log, N=5)

    print("Generating the episode breakdown...")
    breakdown_world_fig, inventories_fig, activity_fig = plotting.breakdown(dense_log)
    _print_episode_summary(dense_log)

    if output_dir is not None:
        output_dir = Path(output_dir)
        figures = {
            "random_episode_final.png": random_episode_fig,
            "dense_episode_final.png": dense_episode_fig,
            "world_t000_t200.png": early_world_fig,
            "world_full_episode.png": complete_world_fig,
            "breakdown_world.png": breakdown_world_fig,
            "inventories_and_labor.png": inventories_fig,
            "movement_and_trades.png": activity_fig,
        }
        for filename, figure in figures.items():
            _save_figure(figure, output_dir, filename)
        print(f"\nSaved {len(figures)} figures to {output_dir.resolve()}")

    if show_plots:
        print("\nClose the Matplotlib windows to finish the example.")
        plt.show()
    else:
        plt.close("all")


if __name__ == "__main__":
    run()
