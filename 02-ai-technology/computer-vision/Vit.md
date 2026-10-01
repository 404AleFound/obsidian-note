![[Pasted image 20261001132527.png]]

```text
origin [B * 3 * 224 * 224]

patches = divide(origin)
patches.size = [B * 196 * 16 * 16 * 3]

patches_flatten = flatten(patches)
patches_flatten.size = [B * 196 * 768]

feature = linearProject(patches_flatten)
feature.size = [B * 196 * 768]

feature_cls = add(CLS, feature)
feature_cls.size = [B * 197 * 768]

feature_cls_positional = positional_feature + feature_cls
feature_cls_positional.size = [B * 197 * 768]

feature_ = transformer_encoder(feature_cls_positional)
feature_.size = [B * 197 * 768]

result = predict(mlp(feature_))
```

