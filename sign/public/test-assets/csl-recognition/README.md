# SignFlow CSL 37 recognition test assets

This package exercises the bundled `csl.pt` model without training or changing its weights.

## Verified uploads

| Asset | Mode | Expected product result |
| --- | --- | --- |
| `images/time.jpg` | Image | `时间` |
| `images/you.jpg` | Image | `你/你的/这个` |
| `videos/time.mp4` | Video | `时间` |
| `videos/you.mp4` | Video | `你/你的/这个` |
| `videos/time-you.mp4` | Video | `时间 你/你的/这个` |

Open `/app/workbench`, choose **SignFlow CSL 37 / 11n-local** in advanced
settings, keep the balanced preset, and upload one of the files above.

Every listed asset was submitted to the local HTTP API with the real model.
Exact job IDs, confidence values, and SHA-256 hashes are recorded in
`manifest.json`.

## Evidence boundary

The workspace contains the trained 37-class weights and training-run
artifacts, but not the original complete `data37_sign` dataset. The two
gesture sources in this package are therefore honest positive smoke tests,
not a full 37-class accuracy claim.
