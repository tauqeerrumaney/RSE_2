rule load_data:
    input:
        "data/EPOC.txt",
    output:
        "temp/filtered_data.feather",
    params:
        mock_flag=lambda wildcards, input, output: "-m" if config["mock"] else "",
    shell:
        """
        python workflow/scripts/load_data.py {input} {output} {params.mock_flag}
        """


rule bandpass_filter:
    input:
        "temp/filtered_data.feather",
    output:
        "temp/bandpassed_data.feather",
    shell:
        """
        python workflow/scripts/bandpass_filter.py {input} {output}
        """


rule truncate_signal:
    input:
        "temp/bandpassed_data.feather",
    output:
        "temp/truncated_data.feather",
    shell:
        """
        python workflow/scripts/truncate_signal.py {input} {output}
        """


rule ica:
    input:
        "temp/truncated_data.feather",
    output:
        "temp/cleaned_epo.fif",
        "results/ica_components.png",
    threads: workflow.cores
    shell:
        """
        python workflow/scripts/ica.py {input} {output} --artifacts {config[artifacts]}
        """


rule denoising:
    input:
        "temp/cleaned_epo.fif",
    output:
        "temp/denoised_epo.fif",
    shell:
        """
        python workflow/scripts/denoising.py {input} {output}
        """


rule feature_extraction:
    input:
        "temp/denoised_epo.fif",
    output:
        "temp/features.npy",
    threads: workflow.cores * 0.5
    shell:
        """
        python workflow/scripts/feature_extraction.py {input} {output}
        """
