# SonarCloud Setup para Analizador Bursátil

## Configuración de SonarCloud

### 1. Crear cuenta en SonarCloud
1. Ve a [sonarcloud.io](https://sonarcloud.io)
2. Inicia sesión con tu cuenta de GitHub
3. Autoriza la aplicación SonarCloud

### 2. Crear proyecto
1. Haz clic en "Create Project"
2. Selecciona "GitHub"
3. Selecciona tu organización `alejandrogcn`
4. Selecciona el repositorio `analizador-bursatil`
5. Configura el proyecto:
   - **Project Key**: `analizador-bursatil`
   - **Organization**: `alejandrogcn`
   - **Project Name**: `Analizador Bursátil`

### 3. Generar token
1. Ve a "My Account" > "Security"
2. Genera un nuevo token
3. Copia el token generado

### 4. Configurar secrets en GitHub
1. Ve a tu repositorio en GitHub
2. Ve a "Settings" > "Secrets and variables" > "Actions"
3. Añade los siguientes secrets:
   - `SONAR_TOKEN`: El token generado en SonarCloud
   - `SONAR_ORGANIZATION`: `alejandrogcn` (opcional)

### 5. Configurar el proyecto
El archivo `sonar-project.properties` ya está configurado con:
- Project key: `analizador-bursatil`
- Organization: `alejandrogcn`
- Fuentes: `src/`
- Exclusions: tests, logs, cache
- Coverage: `coverage.xml`

### 6. Ejecutar análisis
El análisis se ejecutará automáticamente en:
- Push a `main` o `develop`
- Pull requests a `main`

## Resultados
Los resultados estarán disponibles en:
https://sonarcloud.io/project/overview?id=alejandrogcn_analizador-bursatil

## Troubleshooting

### Error: "Failed to query server version"
- Verifica que el token esté correctamente configurado
- Asegúrate de que el proyecto exista en SonarCloud
- Verifica que la organización sea correcta

### Error: "Project not found"
- Verifica que el project key coincida exactamente
- Asegúrate de que el proyecto esté en la organización correcta

### Coverage no aparece
- Verifica que `coverage.xml` se genere correctamente
- Asegúrate de que el path en `sonar-project.properties` sea correcto
