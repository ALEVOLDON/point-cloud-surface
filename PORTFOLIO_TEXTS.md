# Portfolio Texts

## Russian

### Short

`Point Cloud Blob` — процедурный арт-объект, собранный в Blender с помощью Geometry Nodes и Python. Проект генерирует светящуюся point-cloud форму с неоновым градиентом и анимированной деформацией поверхности.

### Medium

`Point Cloud Blob` — это генеративная 3D-сцена в Blender, где органическая форма собирается не из сплошной поверхности, а из тысяч светящихся точек. Я использовал Geometry Nodes для деформации базовой сферы, инстансинга точек по вершинам и анимированной пульсации формы, а через `bpy` автоматизировал сборку сцены, настройку камеры и рендеров. В результате получился проект, который можно воспроизводимо генерировать из кода, использовать как визуальный эксперимент и публиковать как готовый procedural-art asset.

### Long

`Point Cloud Blob` — небольшой procedural-art проект на стыке генеративной графики и технического пайплайна. Задача была воссоздать визуал светящейся объемной формы, похожей на цифровое облако точек, с мягкой органической деформацией и контрастным градиентом на черном фоне.

Технически проект построен вокруг Blender Geometry Nodes: плотная UV-сфера используется как базовая поверхность, затем деформируется несколькими шумовыми слоями, после чего ее вершины преобразуются в points и получают маленький инстанс-сферу. Материал сделан через emission-шейдер с градиентом по оси Z и легкой цветовой вариацией от procedural noise. Дополнительно я автоматизировал сборку через `bpy`, чтобы вся сцена, `.blend`-файл, статичный рендер и последовательность кадров для анимации могли генерироваться воспроизводимо из одного скрипта.

Этот проект хорошо показывает мой подход к procedural-графике: сначала я собираю визуальную систему как набор параметров и зависимостей, затем делаю ее удобной для повторного использования, документации и публикации в виде полноценного репозитория.

## English

### Short

`Point Cloud Blob` is a procedural Blender artwork built with Geometry Nodes and Python. It generates a glowing point-cloud form with a neon gradient and subtle animated surface deformation.

### Medium

`Point Cloud Blob` is a generative 3D scene in Blender where an organic volume is built from thousands of glowing points instead of a solid surface. I used Geometry Nodes to deform a dense sphere, instance point elements across its vertices, and animate the shape with a soft pulse. The scene setup, camera, output files, and renders are automated through `bpy`, making the project reproducible and easy to share as a polished procedural-art asset.

### Long

`Point Cloud Blob` is a small procedural-art project focused on the intersection of generative visuals and production-minded tooling. The goal was to recreate the look of a luminous volumetric shape made of dense points, with soft motion, a strong blue-to-magenta gradient, and a clean black presentation.

From a technical perspective, the project is built around Blender Geometry Nodes. A dense UV sphere serves as the base surface, layered noise displaces the geometry, and the resulting vertices are converted into points that instance a tiny sphere. The material is driven by emission shading, a height-based color ramp, and subtle procedural variation. On top of that, I automated the full scene build with `bpy`, so the `.blend` file, still preview, and animation frame sequence can all be regenerated from a single script.

The project is a good example of how I approach procedural graphics work: I treat the visual result as a system of parameters first, then package it with automation, documentation, and presentation assets so it is reproducible, inspectable, and ready to publish.
