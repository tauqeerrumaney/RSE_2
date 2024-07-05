section_titles = {
    "RQ_1": "Research Question 1",
    "RQ_2": "Research Question 2",
    "RQ_3": "Research Question 3",
    "RQ_4": "Research Question 4",
    "RQ_5": "Research Question 5",
    "denoised_epo_epochs": "Epochs",
    "denoised_epo_psd": "Power Spectral Density",
    "denoised_epo_raw": "Raw Data",
    "denoised_epo_response": "Evoked Response",
    "ica_components": "ICA Components",
}


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
    conda:
        "../envs/generate_plots.yaml"
    shell:
        """
        MNE_BROWSER_BACKEND=matplotlib \
        python workflow/scripts/generate_plots.py {input} {output.epochs_data} {output.epochs_psd} {output.evoked_response} {output.raw_data} &> {log}
        """


rule latex_section_RQ_1:
    input:
        image="results/RQ_1.png",
        json="results/RQ_1.json",
    output:
        "temp/RQ_1_section.tex",
    log:
        "logs/latex_section_RQ_1.txt",
    params:
        textblock="data/textblocks/RQ_1.txt",
        section_title=lambda wildcards, input, output: section_titles["RQ_1"],
    conda:
        "../envs/latex_section.yaml"
    shell:
        """
        python workflow/scripts/latex_section.py {output} "{params.section_title}" \
            --textin {params.textblock} \
            --imagein {input.image} \
            --jsonin {input.json} &> {log}
        """


rule latex_section:
    input:
        "results/{section}.png",
    output:
        "temp/{section}_section.tex",
    log:
        "logs/latex_section_{section}.txt",
    params:
        textblock="data/textblocks/{section}.txt",
        section_title=lambda wildcards, input, output: section_titles[wildcards.section],
    conda:
        "../envs/latex_section.yaml"
    shell:
        """
        python workflow/scripts/latex_section.py {output} "{params.section_title}" \
            --textin {params.textblock} \
            --imagein {input} &> {log}
        """


rule latex_document:
    input:
        "temp/denoised_epo_epochs_section.tex",
        "temp/denoised_epo_psd_section.tex",
        "temp/denoised_epo_raw_section.tex",
        "temp/denoised_epo_response_section.tex",
        "temp/ica_components_section.tex",
        expand("temp/RQ_{section}_section.tex", section=range(1, 6)),
    output:
        tex="temp/report.tex",
        pdf="results/report.pdf",
    log:
        "logs/latex_document.txt",
    conda:
        "../envs/latex_document.yaml"
    shell:
        """
        python workflow/scripts/latex_document.py \
            --latex {output.tex} \
            --pdf {output.pdf} \
            --sections {input} &> {log}
        """
