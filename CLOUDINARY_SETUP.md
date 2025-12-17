# Cloudinary Configuration for Agri KM Zero

## Setup Instructions

1. **Create Free Account**: https://cloudinary.com/users/register/free
2. **Get Credentials**: Dashboard → Settings → API Keys

## Environment Variables (add to Render)

```bash
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

## Free Plan Limits
- 25 GB total storage
- 25 GB bandwidth/month
- 25,000 image transformations/month
- Sufficient for MVP with thousands of images

## Folder Structure on Cloudinary
- `agri_km_zero/products/` - Product images
- `agri_km_zero/profiles/` - Profile photos, logos, covers
