rule RQ_1:
    input:
        "temp/denoised_data.fif",
    output:
        "results/RQ_1.png",
        "results/RQ_1.json",
    shell:
        """
        python workflow/scripts/RQ_1.py {input} {output}
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


rule RQ:
    input:
        "temp/denoised_data.fif",
    output:
        "results/{rule}.png",
    params:
        script="workflow/scripts/{rule}.py",
    shell:
        "python {params.script} {input} {output}"


rule generate_plots:
    input:
        "temp/denoised_data.fif",
    output:
        "results/raw_data.png",
        "results/epochs_data.png",
        "results/epochs_psd.png",
        "results/evoked_response.png",
    shell:
        """
        python workflow/scripts/generate_plots.py {input} results/
        """
