rule rq_1:
    input:
        "temp/denoised_epo.fif",
    output:
        image="results/rq_1.png",
        json="results/rq_1.json",
    log:
        "logs/rq_1.txt",
    conda:
        "../envs/research_question.yaml"
    shell:
        """
        python workflow/scripts/rq_1.py {input} {output.image} {output.json} &> {log}
        """


rule rq_5:
    input:
        "temp/features.npy",
    output:
        "results/rq_5.png",
    log:
        "logs/rq_5.txt",
    conda:
        "../envs/research_question.yaml"
    shell:
        """
        python workflow/scripts/rq_5.py {input} {output} &> {log}
        """


rule rq:
    input:
        "temp/denoised_epo.fif",
    output:
        "results/rq_{rule}.png",
    log:
        "logs/rq_{rule}.txt",
    params:
        script="workflow/scripts/rq_{rule}.py",
    conda:
        "../envs/research_question.yaml"
    shell:
        """
        python {params.script} {input} {output} &> {log}
        """
