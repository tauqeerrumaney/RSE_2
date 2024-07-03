rule RQ_1:
    input:
        "temp/denoised_epo.fif",
    output:
        image="results/RQ_1.png",
        json="results/RQ_1.json",
    shell:
        """
        python workflow/scripts/RQ_1.py {input} {output.image} {output.json}
        """


rule RQ_5:
    input:
        "temp/features.npy",
    output:
        "results/RQ_5.png",
    shell:
        """
        python workflow/scripts/RQ_5.py {input} {output}
        """


rule generate_plots:
    input:
        "temp/{sample}.fif",
    output:
        epochs_data="results/{sample}_epochs.png",
        epochs_psd="results/{sample}_psd.png",
        evoked_response="results/{sample}_response.png",
        raw_data="results/{sample}_raw.png",
    shell:
        """
        python workflow/scripts/generate_plots.py {input} {output.epochs_data} {output.epochs_psd} {output.evoked_response} {output.raw_data}
        """


rule RQ:
    input:
        "temp/denoised_epo.fif",
    output:
        "results/RQ_{rule}.png",
    params:
        script="workflow/scripts/RQ_{rule}.py",
    shell:
        "python {params.script} {input} {output}"
