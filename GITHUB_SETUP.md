# GitHub Setup

Этот файл нужен для быстрого оформления репозитория на GitHub после первого push.

## Repository Name

Рекомендуемое имя:

`point-cloud-blob-blender`

## Short Description

Вариант 1:

`Procedural glowing point-cloud blob made in Blender with Geometry Nodes and Python.`

Вариант 2:

`Blender project for generating a glowing point-cloud blob with Geometry Nodes, bpy, and Eevee bloom.`

## Topics

Рекомендуемые GitHub topics:

- `blender`
- `geometry-nodes`
- `bpy`
- `procedural`
- `point-cloud`
- `generative-art`
- `3d`
- `python`
- `eevee`

## Suggested About Section

Можно вставить в GitHub `About`:

`Procedural glowing point-cloud blob generated in Blender using Geometry Nodes, bpy, and Eevee bloom.`

## Suggested First Release Title

`v1.0.0 - Initial point cloud blob scene`

## Suggested First Release Notes

```text
Initial release of the point cloud blob Blender project.

Includes:
- Procedural Blender scene
- bpy generation script
- Example .blend file
- Preview render
- Full process documentation
- Manual Blender UI step-by-step guide
```

## Optional GitHub CLI Flow

Если установлен `gh`, можно использовать такой порядок:

```powershell
gh repo create point-cloud-blob-blender --public --source . --remote origin --push
```

Если репозиторий уже создан на GitHub:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/point-cloud-blob-blender.git
git push -u origin main
```

