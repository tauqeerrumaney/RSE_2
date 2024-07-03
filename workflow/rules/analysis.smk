rule RQ_1:
    input:
        "temp/denoised_epo.fif",
    output:
        image="results/RQ_1.png",
        json="results/RQ_1.json",
    log:
        "logs/RQ_1.txt",
    shell:
        """
        python workflow/scripts/RQ_1.py {input} {output.image} {output.json} &> {log}
        """


rule RQ_5:
    input:
        "temp/features.npy",
    output:
        "results/RQ_5.png",
    log:
        "logs/RQ_5.txt",
    shell:
        """
        python workflow/scripts/RQ_5.py {input} {output} &> {log}
        """


rule generate_plots:
    input:
        "temp/{sample}.fif",
    output:
        epochs_data="results/{sample}_epochs.png",
        epochs_psd="results/{sample}_psd.png",
        evoked_response="results/{sample}_response.png",
        raw_data="results/{sample}_raw.png",
    log:
        "logs/generate_plots_{sample}.txt",
    shell:
        """
        python workflow/scripts/generate_plots.py {input} {output.epochs_data} {output.epochs_psd} {output.evoked_response} {output.raw_data} &> {log}
        """


rule RQ:
    input:
        "temp/denoised_epo.fif",
    output:
        "results/RQ_{rule}.png",
    log:
        "logs/RQ_{rule}.txt",
    params:
        script="workflow/scripts/RQ_{rule}.py",
    shell:
        """
        python {params.script} {input} {output} &> {log}
        """
