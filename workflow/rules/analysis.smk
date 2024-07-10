rule RQ_1:
    input:
        "temp/denoised_epo.fif",
    output:
        image="results/RQ_1.png",
        json="results/RQ_1.json",
    log:
        "logs/RQ_1.txt",
    conda:
        "../envs/research_question.yaml"
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
    conda:
        "../envs/research_question.yaml"
    shell:
        """
        python workflow/scripts/RQ_5.py {input} {output} &> {log}
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
    conda:
        "../envs/research_question.yaml"
    shell:
        """
        python {params.script} {input} {output} &> {log}
        """
