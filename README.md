# Files for [Secret extraction attacks against obfuscated IQP circuits](https://arxiv.org/abs/2312.10156)

This repository contains the files for the paper [https://arxiv.org/abs/2312.10156](https://arxiv.org/abs/2312.10156).
It is based on commit 11d4c5258ae20d732eee1d141418d23d3a0b7a27 of the repository https://github.com/AlaricCheng/stabilizer_protocol_sim, which in turn is associated with the paper [arXiv:2308.07152](https://arxiv.org/abs/2308.07152).

Attacks described in the new paper can be accessed via the scripts

- radical-attack.py
- lazy-linearity-attack.py
- double-meyer.py
- hamming-razor.py

Various options can be set at the end of the respective files.


- attacks-data/ contains the data generated by the large-scale numerical experiments on the Radical Attack, and various scripts for processing them

- manuscript-figures/ contains code and data to generate the remaining figures

- The various attacks will leave diagnostic data in the log/ folder


For a description of all other files, see https://github.com/AlaricCheng/stabilizer_protocol_sim.

