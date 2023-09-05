# 🚀 Proyecto-ML-Recomendación-Juegos 🎮

Este proyecto se centra en el desarrollo de un sistema de recomendación de videojuegos destinado a los usuarios de Steam, una plataforma de videojuegos internacionalmente reconocida. En mi papel como Ingeniero de MLOps, he liderado la creación de este sistema, partiendo desde la etapa inicial de datos crudos hasta lograr una posible implementación de la API de recomendación. 👾

## Propuesta de trabajo
### Transformaciones:

- Se han leído los conjuntos de datos en formato JSON.
- Se ha llevado a cabo una ETL(Extracción, transformación y carga).
- Los datos transformados se han exportado y guardado como archivos .parquet, los cuales han sido comprimidos con GZIP para optimizar su almacenamiento.

### Analisis de sentimiento

Se usó nlt para el NLP, para así asignar un valor al sentimiento de la reseña y se creó la columna 'sentiment_analysis' tomando el valor '0' si es malo, '1' si es neutral y '2' si es positivo.

### Desarrollo de API
Se desarrolaron las siguientes funciones para realizar consultas en los datos:

- `userdata(User_id: str)`
- `countreviews(YYYY-MM-DD y YYYY-MM-DD: str)`
- `genre(género: str)`
- `userforgenre(género: str)`
- `developer(desarrollador: str)`
- `sentiment_analysis(año: int)`

