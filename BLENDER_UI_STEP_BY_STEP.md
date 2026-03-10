# Blender UI Step By Step

Этот файл описывает, как собрать похожую модель полностью вручную в интерфейсе Blender, без запуска Python-скрипта.

## Что получится

В результате ты соберешь:

- черную сцену
- blob-форму из точек
- голубо-розовый emissive gradient
- мягкое свечение через Eevee Bloom

## Перед стартом

Открой Blender и создай новую пустую сцену.

Если открыт стандартный файл с кубом:

1. Нажми `A`
2. Нажми `X`
3. Подтверди удаление

## Шаг 1. Настрой сцену

Справа открой `Render Properties`.

Поставь:

1. `Render Engine` -> `Eevee`
2. Включи `Bloom`
3. Если доступны параметры Bloom, поставь:
   - `Intensity`: `0.03`
   - `Radius`: `4.5`
   - `Threshold`: `0.6`

Теперь открой `Output Properties`.

Поставь:

1. `Resolution X`: `1536`
2. `Resolution Y`: `1536`
3. `Resolution %`: `100`

Теперь открой `Color Management`.

Поставь:

1. `View Transform`: `Standard`
2. `Look`: `None`
3. `Exposure`: `-1.2`

## Шаг 2. Сделай черный фон

Открой `World Properties`.

Если у мира нет нод:

1. Нажми `Use Nodes`

В секции `Surface` у `Background` поставь:

1. `Color`: черный
2. `Strength`: `0`

## Шаг 3. Создай основную сферу

1. Нажми `Shift + A`
2. Выбери `Mesh -> UV Sphere`

Сразу после добавления, в левом нижнем углу открой панель параметров добавленного объекта.

Поставь:

1. `Segments`: `132`
2. `Rings`: `96`
3. `Radius`: `1.18`

Переименуй объект в `BlobSurface`.

Как переименовать:

1. Выдели объект
2. Нажми `F2`
3. Введи `BlobSurface`

Теперь включи smooth shading:

1. Правый клик по объекту
2. `Shade Smooth`

## Шаг 4. Создай объект-точку

1. Нажми `Shift + A`
2. Выбери `Mesh -> Ico Sphere`

В параметрах объекта поставь:

1. `Subdivisions`: `1`
2. `Radius`: `0.012`

Переименуй его в `DotInstance`.

Спрячь этот объект во viewport:

1. В `Outliner` нажми иконку глаза рядом с `DotInstance`

Важно: объект должен остаться в сцене, потому что он будет использоваться как инстанс в Geometry Nodes.

## Шаг 5. Поверни основную форму

Выдели `BlobSurface`.

Открой панель `Item` клавишей `N`, если она скрыта.

В `Transform` поставь:

1. `Rotation X`: `18°`
2. `Rotation Y`: `-14°`
3. `Rotation Z`: `22°`

И масштаб:

1. `Scale X`: `1.08`
2. `Scale Y`: `1.0`
3. `Scale Z`: `1.04`

## Шаг 6. Создай Geometry Nodes modifier

Выдели `BlobSurface`.

Открой `Modifiers Properties`.

1. Нажми `Add Modifier`
2. Выбери `Geometry Nodes`
3. Нажми `New`

Переименуй нод-группу в `PointCloudBlobNodes`.

Теперь перейди в workspace `Geometry Nodes`.

## Шаг 7. Собери Geometry Nodes

Внутри `PointCloudBlobNodes` тебе нужны такие ноды:

- `Group Input`
- `Group Output`
- `Position`
- `Normal`
- `Set Position`
- `Vector Math` x2
- `Noise Texture` x2
- `Math` x3
- `Map Range`
- `Mesh to Points`
- `Object Info`
- `Instance on Points`
- `Realize Instances`
- `Set Material`

## Шаг 8. Настрой ноды деформации

### 8.1. Добавь входные ноды

Добавь:

1. `Input -> Position`
2. `Input -> Normal`

### 8.2. Добавь два `Vector Math`

Для первого `Vector Math`:

1. `Operation`: `Scale`
2. `Scale`: `1.65`

Для второго `Vector Math`:

1. `Operation`: `Scale`
2. `Scale`: `3.6`

Подключения:

1. `Position` -> первый `Vector Math`
2. `Position` -> второй `Vector Math`

### 8.3. Добавь два `Noise Texture`

Для первого `Noise Texture`:

1. `Noise Dimensions`: `4D`
2. `Scale`: `1.0`
3. `Detail`: `7.0`
4. `Roughness`: `0.42`
5. `W`: `0.18`

Для второго `Noise Texture`:

1. `Noise Dimensions`: `4D`
2. `Scale`: `1.0`
3. `Detail`: `3.0`
4. `Roughness`: `0.55`
5. `W`: `4.7`

Подключения:

1. первый `Vector Math` -> первый `Noise Texture`
2. второй `Vector Math` -> второй `Noise Texture`

### 8.4. Добавь `Math` для силы шумов

Добавь два `Math`.

У обоих:

1. `Operation`: `Multiply`

Для первого:

1. второй параметр: `0.42`

Для второго:

1. второй параметр: `0.16`

Подключения:

1. `Fac` первого `Noise Texture` -> первый `Math`
2. `Fac` второго `Noise Texture` -> второй `Math`

### 8.5. Сложи шумы

Добавь третий `Math`.

Поставь:

1. `Operation`: `Add`

Подключения:

1. выход первого `Math` -> вход 1 `Add`
2. выход второго `Math` -> вход 2 `Add`

### 8.6. Добавь `Map Range`

Поставь:

1. `From Min`: `0.0`
2. `From Max`: `0.58`
3. `To Min`: `-0.24`
4. `To Max`: `0.36`
5. `Clamp`: выключить

Подключение:

1. `Add` -> `Map Range`

### 8.7. Умножь нормаль на силу смещения

Добавь еще один `Vector Math`.

Поставь:

1. `Operation`: `Scale`

Подключения:

1. `Normal` -> этот `Vector Math`
2. `Map Range` -> `Scale` этого `Vector Math`

### 8.8. Смещение поверхности

Добавь `Set Position`.

Подключения:

1. `Group Input -> Geometry` -> `Set Position -> Geometry`
2. выход последнего `Vector Math` -> `Set Position -> Offset`

На этом этапе форма уже должна стать неровной.

## Шаг 9. Преврати вершины в точки

Добавь `Mesh to Points`.

Поставь:

1. `Mode`: `Vertices`
2. `Radius`: `0.018`

Подключение:

1. `Set Position -> Geometry` -> `Mesh to Points -> Mesh`

## Шаг 10. Заинстансь маленькую сферу

Добавь `Object Info`.

В поле `Object` выбери `DotInstance`.

Если есть `Transform Space`, поставь:

1. `Relative`

Теперь добавь `Instance on Points`.

Подключения:

1. `Mesh to Points -> Points` -> `Instance on Points -> Points`
2. `Object Info -> Geometry` -> `Instance on Points -> Instance`

## Шаг 11. Реализуй инстансы

Добавь `Realize Instances`.

Подключение:

1. `Instance on Points -> Instances` -> `Realize Instances -> Geometry`

## Шаг 12. Создай материал

Перейди в workspace `Shading`.

Выдели `BlobSurface`.

Создай новый материал и назови его `PointGlow`.

Нужные ноды:

- `Material Output`
- `Emission`
- `Geometry`
- `Separate XYZ`
- `Map Range`
- `Noise Texture`
- `Math` x2
- `Color Ramp`
- `Value`

## Шаг 13. Собери материал

### 13.1. Позиция и градиент по высоте

Добавь `Geometry`.

Из него возьми `Position`.

Добавь `Separate XYZ`.

Подключи:

1. `Geometry -> Position` -> `Separate XYZ`

Добавь `Map Range`.

Поставь:

1. `From Min`: `-1.4`
2. `From Max`: `1.4`
3. `To Min`: `0.0`
4. `To Max`: `1.0`
5. `Clamp`: включить

Подключи:

1. `Separate XYZ -> Z` -> `Map Range -> Value`

### 13.2. Добавь легкий шум в цвет

Добавь `Noise Texture`.

Поставь:

1. `Scale`: `1.8`
2. `Detail`: `5.4`
3. `Roughness`: `0.45`

Подключи:

1. `Geometry -> Position` -> `Noise Texture -> Vector`

Добавь `Math` с операцией `Multiply`.

Поставь:

1. второй параметр: `0.12`

Подключи:

1. `Noise Texture -> Fac` -> `Math Multiply`

Добавь еще один `Math` с операцией `Add`.

Включи `Clamp`.

Подключи:

1. `Map Range -> Result` -> вход 1 `Add`
2. `Math Multiply` -> вход 2 `Add`

### 13.3. Сделай цветовой градиент

Добавь `Color Ramp`.

Поставь 2 точки:

1. Первая:
   - `Position`: `0.12`
   - цвет: `(0.9, 0.28, 1.0)`
2. Вторая:
   - `Position`: `0.9`
   - цвет: `(0.16, 0.58, 1.0)`

Подключи:

1. `Add` -> `Color Ramp -> Fac`

### 13.4. Настрой Emission

Добавь `Emission`.

Добавь `Value`.

Поставь:

1. `Value`: `2.8`

Подключения:

1. `Color Ramp -> Color` -> `Emission -> Color`
2. `Value` -> `Emission -> Strength`
3. `Emission` -> `Material Output -> Surface`

## Шаг 14. Назначь материал через Geometry Nodes

Вернись в workspace `Geometry Nodes`.

Добавь `Set Material`.

В поле `Material` выбери `PointGlow`.

Подключения:

1. `Realize Instances -> Geometry` -> `Set Material -> Geometry`
2. `Set Material -> Geometry` -> `Group Output -> Geometry`

После этого точки должны стать светящимися и цветными.

## Шаг 15. Настрой камеру

1. Нажми `Shift + A`
2. Выбери `Camera`

Поставь камере:

1. `Location X`: `0.0`
2. `Location Y`: `-6.4`
3. `Location Z`: `0.9`

Поставь вращение:

1. `Rotation X`: `82°`
2. `Rotation Y`: `0°`
3. `Rotation Z`: `0°`

Поставь:

1. `Lens`: `62`

Включи Depth of Field:

1. `Focus Distance`: `6.1`
2. `F-Stop`: `2.8`

## Шаг 16. Сделай target для камеры

1. Нажми `Shift + A`
2. Выбери `Empty -> Plain Axes`

Переименуй в `CameraTarget`.

Поставь позицию:

1. `X`: `0.0`
2. `Y`: `0.0`
3. `Z`: `0.08`

Теперь выдели камеру.

Во вкладке `Constraints`:

1. `Add Object Constraint`
2. Выбери `Track To`

Поставь:

1. `Target`: `CameraTarget`
2. `To`: `-Z`
3. `Up`: `Y`

## Шаг 17. Посмотри через камеру

1. Нажми `Numpad 0`

Если объекта слишком много или мало в кадре:

1. двигай камеру по `Y`
2. меняй `Lens`
3. чуть сдвигай `CameraTarget` по `Z`

## Шаг 18. Рендер

Для превью:

1. Переключи viewport в `Rendered`

Для финального изображения:

1. Нажми `F12`

Для сохранения:

1. В окне рендера выбери `Image -> Save As`

## Если получается не так

### Слишком сплошная поверхность

Уменьши:

- радиус `DotInstance`
- `Emission Strength`
- `Bloom Intensity`

### Слишком мало точек

Увеличь:

- `Segments` и `Rings` у `BlobSurface`

### Форма слишком гладкая

Увеличь:

- множители шумов
- диапазон в `Map Range` внутри Geometry Nodes

### Цвет слишком белый

Уменьши:

- `Emission Strength`
- `Bloom Intensity`
- `Exposure`

### Цвета не похожи на референс

Поменяй цвета в `Color Ramp`.

## Минимальная схема соединений Geometry Nodes

В сокращенном виде цепочка такая:

`Group Input`
-> `Set Position`
-> `Mesh to Points`
-> `Instance on Points`
-> `Realize Instances`
-> `Set Material`
-> `Group Output`

Для смещения:

`Position`
-> `Vector Math`
-> `Noise Texture`
-> `Math`

`Position`
-> `Vector Math`
-> `Noise Texture`
-> `Math`

оба шума
-> `Add`
-> `Map Range`
-> масштаб по `Normal`
-> `Set Position Offset`

## Минимальная схема соединений материала

`Geometry Position`
-> `Separate XYZ`
-> `Z`
-> `Map Range`
-> `Add noise`
-> `Color Ramp`
-> `Emission`
-> `Material Output`

## Что можно сделать следующим шагом

Если хочешь, я могу еще добавить:

- файл со схемой нод в виде ASCII-диаграммы
- файл с настройкой анимации blob
- файл с экспортом в `glb` или `fbx`
- файл с версией для Cycles
