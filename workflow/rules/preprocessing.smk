rule load_data:
    input:
        "data/EPOC.txt",
    output:
        "temp/filtered_data.feather",
    params:
        mock_flag=lambda wildcards, input, output: "-m" if config["mock"] else "",
    log:
        "logs/load_data.txt",
    conda:
        "../envs/load_data.yaml"
    shell:
        """
        python workflow/scripts/load_data.py {input} {output} {params.mock_flag} &> {log}
        """


rule bandpass_filter:
    input:
        "temp/filtered_data.feather",
    output:
        "temp/bandpassed_data.feather",
    log:
        "logs/bandpass_filter.txt",
    conda:
        "../envs/bandpass_filter.yaml"
    shell:
        """
        python workflow/scripts/bandpass_filter.py {input} {output} &> {log}
        """


rule truncate_signal:
    input:
        "temp/bandpassed_data.feather",
    output:
        "temp/truncated_data.feather",
    log:
        "logs/truncate_signal.txt",
    conda:
        "../envs/truncate_signal.yaml"
    shell:
        """
        python workflow/scripts/truncate_signal.py {input} {output} &> {log}
        """


rule ica:
    input:
        "temp/truncated_data.feather",
    output:
        "temp/cleaned_epo.fif",
        "results/ica_components.png",
    log:
        "logs/ica.txt",
    params:
        artifacts=lambda wildcards, input, output: config["artifacts"],
    conda:
        "../envs/ica.yaml"
    threads: workflow.cores
    shell:
        """
        python workflow/scripts/ica.py {input} {output} --artifacts {params.artifacts} &> {log}
        """


rule denoising:
    input:
        "temp/cleaned_epo.fif",
    output:
        "temp/denoised_epo.fif",
    log:
        "logs/denoising.txt",
    conda:
        "../envs/denoising.yaml"
    shell:
        """
        python workflow/scripts/denoising.py {input} {output} &> {log}
        """


rule feature_extraction:
    input:
        "temp/denoised_epo.fif",
    output:
        "temp/features.npy",
    log:
        "logs/feature_extraction.txt",
    conda:
        "../envs/feature_extraction.yaml"
    threads: workflow.cores * 0.5
    shell:
        """
        python workflow/scripts/feature_extraction.py {input} {output} &> {log}
        """
