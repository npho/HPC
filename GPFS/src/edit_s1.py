s=open('script.py').read()
start=s.index('("s1", ['); end=s.index('("s2", [')
new='''("s1", [
 "The story starts at IBM in the early nineteen nineties, with two research efforts. At the Watson lab, Vesta explored how parallel programs could partition files across disks. At Almaden, in California, Tiger Shark was built for something that sounds unrelated: streaming multimedia.",
 "But video means many steady streams, served from an array of disks. So you stripe everything, and never let one disk become the hot spot. That's exactly what a scientific code writing a checkpoint wants, too.",
 "The two lineages merged into G P F S, around nineteen ninety eight, with the standard Unix interface, so ordinary programs just worked. The foundational document is a two thousand two paper at the FAST conference, from two Almaden researchers. Its three big ideas, shared disks, wide striping, and distributed locking, are still the skeleton of the system.",
 "It describes A-S-C-I White, a five hundred twelve node machine with a hundred and forty terabytes of disk, where sixteen nodes could drive the machine's entire twelve gigabytes per second of I O bandwidth. Hold on to those numbers. We'll compare them with a modern system later.",
 "Since then: Spectrum Scale in twenty fifteen, when IBM put that prefix on its storage products, and Storage Scale in early twenty twenty three, when the prefix was dropped. Same lineage, same core design.",
]),
'''
open('script.py','w').write(s[:start]+new+s[end:])
