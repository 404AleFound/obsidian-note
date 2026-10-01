![[Pasted image 20261001132527.png]]

```text
origin [B * 3 * 224 * 224]

patches = divide(origin)
patches.size = [B * 196 * 16 * 16 * 3]

patches_flatten = flatten(patches)
patches_flatten.size = [B * 196 * 768]

features = linearProject(patches_flatten)


```