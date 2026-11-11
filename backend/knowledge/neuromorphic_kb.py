"""
Curated knowledge base for Neuromorphic AI research.
Used by the Recall agent to ground claims and reduce hallucinations.
"""

NEUROMORPHIC_KNOWLEDGE = {
    "core_concepts": {
        "neuromorphic_computing": (
            "Neuromorphic computing is a brain-inspired approach to computing that uses "
            "spiking neural networks, event-driven processing, and specialized hardware "
            "to achieve high energy efficiency and real-time processing for sensory and cognitive tasks."
        ),
        "spiking_neural_networks": (
            "Spiking Neural Networks (SNNs) communicate via discrete spikes (action potentials) "
            "rather than continuous activations. Timing of spikes carries information. "
            "Common neuron models: Leaky Integrate-and-Fire (LIF), Adaptive Exponential (AdEx), Hodgkin-Huxley."
        ),
        "event_driven": (
            "Event-driven processing means computation only occurs when spikes arrive, "
            "leading to sparse activity and very low power consumption compared to always-on ANNs."
        ),
        "synaptic_plasticity": (
            "Key mechanisms include Spike-Timing-Dependent Plasticity (STDP), "
            "which strengthens or weakens synapses based on the relative timing of pre- and post-synaptic spikes."
        ),
    },
    "hardware": {
        "intel_loihi": (
            "Intel Loihi is a neuromorphic research chip that supports on-chip learning, "
            "programmable synaptic plasticity, and hierarchical connectivity. Loihi 2 improves density and features."
        ),
        "ibm_truenorth": (
            "IBM TrueNorth is an early neuromorphic chip with 1 million neurons and 256 million synapses, "
            "designed for extremely low power pattern recognition tasks. It does not support on-chip learning in the same flexible way as Loihi."
        ),
        "brainscales": (
            "BrainScaleS (Heidelberg) is a mixed-signal analog neuromorphic system that accelerates "
            "biological time constants, enabling fast emulation of neural networks."
        ),
        "spinnaker": (
            "SpiNNaker (University of Manchester) is a large-scale digital neuromorphic platform "
            "based on many ARM cores, designed for real-time simulation of large SNNs."
        ),
        "memristors": (
            "Memristors are two-terminal devices whose resistance depends on the history of current. "
            "They are used as synaptic elements in analog neuromorphic hardware because they can implement "
            "plasticity and store weight in a compact, non-volatile way."
        ),
    },
    "algorithms_and_training": {
        "surrogate_gradient": (
            "Because the spike function is non-differentiable, surrogate gradient methods "
            "(e.g., SuperSpike, SLAYER, surrogate derivatives of Heaviside) are widely used "
            "to train deep SNNs with backpropagation-like algorithms."
        ),
        "conversion": (
            "ANN-to-SNN conversion maps trained rate-based networks to spiking networks, "
            "often using rate coding or temporal coding. It can achieve competitive accuracy "
            "but may require longer simulation times and careful threshold/weight scaling."
        ),
        "direct_training": (
            "Direct training of SNNs uses surrogate gradients or evolutionary / reward-modulated rules. "
            "It can exploit temporal dynamics better than conversion but is often more computationally expensive."
        ),
        "stdp": (
            "STDP is a local, unsupervised learning rule. Variants include triplet STDP, "
            "reward-modulated STDP, and supervised STDP approximations."
        ),
    },
    "common_mistakes_and_myths": [
        "Claiming that SNNs are always more accurate than ANNs — in practice SNNs often lag in accuracy on static image benchmarks unless carefully trained.",
        "Saying neuromorphic chips are ready to replace GPUs for all deep learning — they excel at sparse, event-driven, low-power workloads, not dense matrix multiplies.",
        "Confusing rate coding with temporal coding — rate coding uses average spike rate; temporal coding uses precise spike times or order.",
        "Assuming all neuromorphic hardware supports online learning — TrueNorth largely does not; Loihi does.",
        "Overstating biological realism — most practical SNNs use highly simplified neuron models, not full Hodgkin-Huxley dynamics.",
        "Claiming zero energy for idle neurons without noting overhead of the supporting digital/analog fabric.",
    ],
    "key_papers_and_facts": {
        "maass_1997": "Wolfgang Maass formalized the computational power of spiking neurons.",
        "davies_2018": "Mike Davies et al. introduced Loihi in IEEE Micro / Nature papers around 2018.",
        "indiveri_liu": "Giacomo Indiveri and Shih-Chii Liu have extensive work on neuromorphic sensors and circuits.",
        "energy": "Neuromorphic systems can achieve orders-of-magnitude better energy efficiency (ops/J or inferences/J) than GPUs for certain sparse workloads.",
    },
    "coding_schemes": {
        "rate_coding": "Information is encoded in the average number of spikes over a time window.",
        "temporal_coding": "Information is carried by the precise timing of spikes (latency coding, rank-order coding, phase coding).",
        "population_coding": "Information is distributed across a population of neurons.",
    },
}


def search_knowledge(query: str, top_k: int = 5) -> list[dict]:
    """Simple keyword-based retrieval from the knowledge base."""
    query_lower = query.lower()
    results = []

    # Flatten knowledge
    for category, content in NEUROMORPHIC_KNOWLEDGE.items():
        if category == "common_mistakes_and_myths":
            for mistake in content:
                if any(term in mistake.lower() for term in query_lower.split()):
                    results.append({
                        "source": "common_mistakes",
                        "content": mistake,
                        "relevance": "high" if any(t in mistake.lower() for t in ["snn", "loihi", "stdp", "energy"]) else "medium"
                    })
        elif isinstance(content, dict):
            for key, value in content.items():
                text = f"{key}: {value}".lower()
                score = sum(1 for term in query_lower.split() if term in text)
                if score > 0:
                    results.append({
                        "source": f"{category}.{key}",
                        "content": value,
                        "relevance": "high" if score >= 2 else "medium"
                    })

    # Sort by relevance
    results.sort(key=lambda x: 0 if x["relevance"] == "high" else 1)
    return results[:top_k]


def get_all_mistakes() -> list[str]:
    return NEUROMORPHIC_KNOWLEDGE["common_mistakes_and_myths"]
