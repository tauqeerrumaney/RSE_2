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
            python workflow/scripts/generate_plots.py {input} \
            {output.epochs_data} {output.epochs_psd} {output.evoked_response} {output.raw_data} &> {log}
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
        conditional_json=lambda wildcards, input, output: (
            "--jsonin results/rq_1.json" if wildcards.section == "rq_1" else ""
        ),
    conda:
        "../envs/latex_section.yaml"
    shell:
        """
        python workflow/scripts/latex_section.py {output} "{params.section_title}" \
            {params.conditional_json} \
            --textin {params.textblock} \
            --imagein {input} &> {log}
        """


rule latex_document:
    input:
        expand("temp/{section}_section.tex", section=section_titles.keys()),
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
