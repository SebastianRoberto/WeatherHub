import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useI18nStore = defineStore('i18n', () => {
  const currentLanguage = ref('es')
  
  // Traducciones
  const translations = {
    es: {
      // Navegación
      nav: {
        dashboard: 'Dashboard',
        history: 'Historial',
        compare: 'Comparar',
        alerts: 'Alertas',
        profile: 'Perfil',
        login: 'Iniciar sesión',
        register: 'Registrarse',
        logout: 'Salir'
      },
      
      // Autenticación
      auth: {
        login: 'Iniciar sesión',
        register: 'Registrarse',
        email: 'Email',
        password: 'Contraseña',
        confirmPassword: 'Confirmar contraseña',
        fullName: 'Nombre completo',
        loginButton: 'Iniciar sesión',
        registerButton: 'Crear cuenta',
        loginTitle: 'Inicia sesión en WeatherHub',
        registerTitle: 'Crea tu cuenta en WeatherHub',
        loginSubtitle: 'Accede a tu panel meteorológico personal',
        registerSubtitle: 'Únete a WeatherHub y comienza a monitorear el clima',
        forgotPassword: '¿Olvidaste tu contraseña?',
        noAccount: '¿No tienes cuenta?',
        haveAccount: '¿Ya tienes cuenta?',
        loginSuccess: 'Sesión iniciada correctamente',
        registerSuccess: 'Cuenta creada exitosamente',
        loginError: 'Error al iniciar sesión',
        registerError: 'Error al crear cuenta',
        invalidEmail: 'Por favor ingresa un email válido',
        passwordTooShort: 'La contraseña debe tener al menos 6 caracteres',
        passwordsNotMatch: 'Las contraseñas no coinciden',
        emailRequired: 'El email es requerido',
        passwordRequired: 'La contraseña es requerida',
        nameRequired: 'El nombre es requerido'
      },
      
      // Dashboard
      dashboard: {
        title: 'Dashboard',
        welcome: 'Bienvenido',
        currentWeather: 'Clima actual',
        favorites: 'Ciudades favoritas',
        addFavorite: 'Agregar a favoritos',
        removeFavorite: 'Quitar de favoritos',
        lastUpdate: 'Última actualización',
        temperature: 'Temperatura',
        humidity: 'Humedad',
        pressure: 'Presión',
        wind: 'Viento',
        visibility: 'Visibilidad',
        feelsLike: 'Sensación térmica',
        weatherDescription: 'Descripción del clima'
      },
      
      // Historial
      history: {
        title: 'Historial',
        subtitle: 'Datos históricos meteorológicos',
        selectCity: 'Seleccionar ciudad',
        selectPeriod: 'Seleccionar período',
        selectMetrics: 'Seleccionar métricas',
        search: 'Buscar',
        loading: 'Cargando datos históricos...',
        loadingMetric: 'Cargando {metric}...',
        noData: 'Sin datos históricos',
        noDataMessage: 'No hay datos históricos disponibles para esta ciudad. Intenta con otra ciudad o un rango de fechas diferente.',
        dateRange: 'Rango de fechas',
        lastDays: 'Últimos {days} días',
        customRange: 'Rango personalizado',
        startDate: 'Fecha inicio',
        endDate: 'Fecha fin',
        temperature: 'Temperatura',
        humidity: 'Humedad',
        pressure: 'Presión',
        wind: 'Viento',
        description: 'Descripción',
        maxTemp: 'Temperatura máxima',
        minTemp: 'Temperatura mínima',
        avgHumidity: 'Humedad promedio',
        evolution: 'Evolución del tiempo',
        detailedData: 'Datos detallados',
        filter: 'Filtrar',
        image: 'Imagen'
      },
      
      // Comparar
      compare: {
        title: 'Comparación de Ciudades',
        subtitle: 'Compara datos meteorológicos entre ciudades',
        selectCities: 'Seleccionar ciudades para comparar',
        addCity: 'Añadir ciudad...',
        addCityButton: 'Añadir',
        favorites: 'Ciudades favoritas',
        period: 'Período',
        metric: 'Métrica',
        lastDays: 'Últimos {days} días',
        temperature: 'Temperatura',
        humidity: 'Humedad',
        pressure: 'Presión',
        wind: 'Viento',
        loading: 'Cargando datos de comparación...',
        loadingMetric: 'Cargando {metric}...',
        noData: 'Sin datos de comparación',
        noDataMessage: 'Seleccione al menos dos ciudades para comparar sus datos meteorológicos.',
        chartTitle: 'Comparación de {metric}',
        citySummary: 'Resumen por ciudad',
        average: 'Promedio',
        maximum: 'Máximo',
        minimum: 'Mínimo',
        differences: 'Análisis de diferencias',
        comparison: 'Comparación',
        avgDifference: 'Diferencia promedio',
        maxDifference: 'Diferencia máxima',
        minDifference: 'Diferencia mínima',
        image: 'Imagen'
      },
      
      // Alertas
      alerts: {
        title: 'Gestión de Alertas',
        subtitle: 'Configura alertas meteorológicas personalizadas',
        newAlert: 'Nueva Alerta',
        viewHistory: 'Ver Historial',
        createAlert: 'Crear Nueva Alerta',
        close: 'Cerrar',
        city: 'Ciudad',
        selectCity: 'Selecciona una ciudad',
        metric: 'Métrica',
        condition: 'Condición',
        threshold: 'Umbral',
        greaterThan: 'Mayor que',
        lessThan: 'Menor que',
        greaterEqual: 'Mayor o igual',
        lessEqual: 'Menor o igual',
        temperature: 'Temperatura',
        humidity: 'Humedad',
        wind: 'Viento',
        pressure: 'Presión',
        cancel: 'Cancelar',
        create: 'Crear Alerta',
        myAlerts: 'Mis Alertas',
        alertsConfigured: '{count} alertas configuradas',
        loading: 'Cargando alertas...',
        noAlerts: 'No tienes alertas configuradas',
        noAlertsMessage: 'Crea una alerta para recibir notificaciones cuando las condiciones meteorológicas cumplan ciertos criterios.',
        createFirstAlert: 'Crear Primera Alerta',
        alertHistory: 'Historial de Alertas',
        viewActiveAlerts: 'Ver Alertas Activas',
        loadingHistory: 'Cargando historial...',
        noHistory: 'No hay historial de alertas',
        noHistoryMessage: 'Cuando tus alertas se activen, aparecerán aquí.',
        date: 'Fecha',
        city: 'Ciudad',
        metric: 'Métrica',
        condition: 'Condición',
        observedValue: 'Valor Observado',
        active: 'Activa',
        paused: 'Pausada',
        resume: 'Reanudar',
        pause: 'Pausar',
        delete: 'Eliminar',
        confirmDelete: '¿Estás seguro de que quieres eliminar esta alerta?',
        howWork: '¿Cómo funcionan las alertas?',
        howWorkMessage: 'Las alertas te permiten monitorear condiciones meteorológicas específicas para tus ciudades favoritas.',
        step1: 'Selecciona una ciudad',
        step1Desc: 'Elige una de tus ciudades favoritas para monitorear.',
        step2: 'Define una condición',
        step2Desc: 'Especifica qué métrica (temperatura, humedad, etc.) quieres monitorear y bajo qué condiciones.',
        step3: 'Recibe notificaciones',
        step3Desc: 'Cuando las condiciones se cumplan, se registrará en el historial de alertas.'
      },
      
      // Perfil
      profile: {
        title: 'Perfil de Usuario',
        subtitle: 'Gestiona tu información personal y preferencias',
        personalInfo: 'Información personal',
        changePassword: 'Cambiar contraseña',
        name: 'Nombre',
        email: 'Email',
        memberSince: 'Miembro desde',
        preferences: 'Preferencias',
        language: 'Idioma',
        languageDescription: 'Selecciona el idioma de la interfaz.',
        theme: 'Tema',
        light: 'Claro',
        dark: 'Oscuro',
        system: 'Sistema',
        units: 'Unidades de temperatura',
        unitsDescription: 'Selecciona la unidad de temperatura que prefieres para visualizar los datos meteorológicos.',
        celsius: 'Celsius',
        fahrenheit: 'Fahrenheit',
        kelvin: 'Kelvin',
        save: 'Guardar cambios',
        cancel: 'Cancelar',
        saved: 'Cambios guardados',
        error: 'Error al guardar',
        loading: 'Guardando...'
      },
      
      // Común
      common: {
        loading: 'Cargando...',
        error: 'Error',
        success: 'Éxito',
        cancel: 'Cancelar',
        save: 'Guardar',
        delete: 'Eliminar',
        edit: 'Editar',
        close: 'Cerrar',
        back: 'Atrás',
        next: 'Siguiente',
        previous: 'Anterior',
        search: 'Buscar',
        filter: 'Filtrar',
        export: 'Exportar',
        download: 'Descargar',
        refresh: 'Actualizar',
        retry: 'Reintentar',
        confirm: 'Confirmar',
        yes: 'Sí',
        no: 'No',
        ok: 'OK',
        today: 'Hoy',
        yesterday: 'Ayer',
        tomorrow: 'Mañana',
        monday: 'Lunes',
        tuesday: 'Martes',
        wednesday: 'Miércoles',
        thursday: 'Jueves',
        friday: 'Viernes',
        saturday: 'Sábado',
        sunday: 'Domingo',
        january: 'Enero',
        february: 'Febrero',
        march: 'Marzo',
        april: 'Abril',
        may: 'Mayo',
        june: 'Junio',
        july: 'Julio',
        august: 'Agosto',
        september: 'Septiembre',
        october: 'Octubre',
        november: 'Noviembre',
        december: 'Diciembre'
      }
    },
    
    en: {
      // Navigation
      nav: {
        dashboard: 'Dashboard',
        history: 'History',
        compare: 'Compare',
        alerts: 'Alerts',
        profile: 'Profile',
        login: 'Sign In',
        register: 'Sign Up',
        logout: 'Logout'
      },
      
      // Authentication
      auth: {
        login: 'Sign In',
        register: 'Sign Up',
        email: 'Email',
        password: 'Password',
        confirmPassword: 'Confirm Password',
        fullName: 'Full Name',
        loginButton: 'Sign In',
        registerButton: 'Create Account',
        loginTitle: 'Sign in to WeatherHub',
        registerTitle: 'Create your WeatherHub account',
        loginSubtitle: 'Access your personal weather dashboard',
        registerSubtitle: 'Join WeatherHub and start monitoring the weather',
        forgotPassword: 'Forgot your password?',
        noAccount: "Don't have an account?",
        haveAccount: 'Already have an account?',
        loginSuccess: 'Successfully signed in',
        registerSuccess: 'Account created successfully',
        loginError: 'Error signing in',
        registerError: 'Error creating account',
        invalidEmail: 'Please enter a valid email',
        passwordTooShort: 'Password must be at least 6 characters',
        passwordsNotMatch: 'Passwords do not match',
        emailRequired: 'Email is required',
        passwordRequired: 'Password is required',
        nameRequired: 'Name is required'
      },
      
      // Dashboard
      dashboard: {
        title: 'Dashboard',
        welcome: 'Welcome',
        currentWeather: 'Current Weather',
        favorites: 'Favorite Cities',
        addFavorite: 'Add to favorites',
        removeFavorite: 'Remove from favorites',
        lastUpdate: 'Last update',
        temperature: 'Temperature',
        humidity: 'Humidity',
        pressure: 'Pressure',
        wind: 'Wind',
        visibility: 'Visibility',
        feelsLike: 'Feels like',
        weatherDescription: 'Weather description'
      },
      
      // History
      history: {
        title: 'History',
        subtitle: 'Historical weather data',
        selectCity: 'Select city',
        selectPeriod: 'Select period',
        selectMetrics: 'Select metrics',
        search: 'Search',
        loading: 'Loading historical data...',
        loadingMetric: 'Loading {metric}...',
        noData: 'No historical data',
        noDataMessage: 'No historical data available for this city. Try with another city or a different date range.',
        dateRange: 'Date range',
        lastDays: 'Last {days} days',
        customRange: 'Custom range',
        startDate: 'Start date',
        endDate: 'End date',
        temperature: 'Temperature',
        humidity: 'Humidity',
        pressure: 'Pressure',
        wind: 'Wind',
        description: 'Description',
        maxTemp: 'Maximum temperature',
        minTemp: 'Minimum temperature',
        avgHumidity: 'Average humidity',
        evolution: 'Weather evolution',
        detailedData: 'Detailed data',
        filter: 'Filter',
        image: 'Image'
      },
      
      // Compare
      compare: {
        title: 'City Comparison',
        subtitle: 'Compare weather data between cities',
        selectCities: 'Select cities to compare',
        addCity: 'Add city...',
        addCityButton: 'Add',
        favorites: 'Favorite cities',
        period: 'Period',
        metric: 'Metric',
        lastDays: 'Last {days} days',
        temperature: 'Temperature',
        humidity: 'Humidity',
        pressure: 'Pressure',
        wind: 'Wind',
        loading: 'Loading comparison data...',
        loadingMetric: 'Loading {metric}...',
        noData: 'No comparison data',
        noDataMessage: 'Select at least two cities to compare their weather data.',
        chartTitle: '{metric} Comparison',
        citySummary: 'Summary by city',
        average: 'Average',
        maximum: 'Maximum',
        minimum: 'Minimum',
        differences: 'Difference analysis',
        comparison: 'Comparison',
        avgDifference: 'Average difference',
        maxDifference: 'Maximum difference',
        minDifference: 'Minimum difference',
        image: 'Image'
      },
      
      // Alerts
      alerts: {
        title: 'Alert Management',
        subtitle: 'Configure personalized weather alerts',
        newAlert: 'New Alert',
        viewHistory: 'View History',
        createAlert: 'Create New Alert',
        close: 'Close',
        city: 'City',
        selectCity: 'Select a city',
        metric: 'Metric',
        condition: 'Condition',
        threshold: 'Threshold',
        greaterThan: 'Greater than',
        lessThan: 'Less than',
        greaterEqual: 'Greater or equal',
        lessEqual: 'Less or equal',
        temperature: 'Temperature',
        humidity: 'Humidity',
        wind: 'Wind',
        pressure: 'Pressure',
        cancel: 'Cancel',
        create: 'Create Alert',
        myAlerts: 'My Alerts',
        alertsConfigured: '{count} alerts configured',
        loading: 'Loading alerts...',
        noAlerts: 'No alerts configured',
        noAlertsMessage: 'Create an alert to receive notifications when weather conditions meet certain criteria.',
        createFirstAlert: 'Create First Alert',
        alertHistory: 'Alert History',
        viewActiveAlerts: 'View Active Alerts',
        loadingHistory: 'Loading history...',
        noHistory: 'No alert history',
        noHistoryMessage: 'When your alerts are triggered, they will appear here.',
        date: 'Date',
        city: 'City',
        metric: 'Metric',
        condition: 'Condition',
        observedValue: 'Observed Value',
        active: 'Active',
        paused: 'Paused',
        resume: 'Resume',
        pause: 'Pause',
        delete: 'Delete',
        confirmDelete: 'Are you sure you want to delete this alert?',
        howWork: 'How do alerts work?',
        howWorkMessage: 'Alerts allow you to monitor specific weather conditions for your favorite cities.',
        step1: 'Select a city',
        step1Desc: 'Choose one of your favorite cities to monitor.',
        step2: 'Define a condition',
        step2Desc: 'Specify which metric (temperature, humidity, etc.) you want to monitor and under what conditions.',
        step3: 'Receive notifications',
        step3Desc: 'When conditions are met, it will be recorded in the alert history.'
      },
      
      // Profile
      profile: {
        title: 'User Profile',
        subtitle: 'Manage your personal information and preferences',
        personalInfo: 'Personal information',
        changePassword: 'Change Password',
        name: 'Name',
        email: 'Email',
        memberSince: 'Member since',
        preferences: 'Preferences',
        language: 'Language',
        languageDescription: 'Select the interface language.',
        theme: 'Theme',
        light: 'Light',
        dark: 'Dark',
        system: 'System',
        units: 'Temperature units',
        unitsDescription: 'Select the temperature unit you prefer to display meteorological data.',
        celsius: 'Celsius',
        fahrenheit: 'Fahrenheit',
        kelvin: 'Kelvin',
        save: 'Save changes',
        cancel: 'Cancel',
        saved: 'Changes saved',
        error: 'Error saving',
        loading: 'Saving...'
      },
      
      // Common
      common: {
        loading: 'Loading...',
        error: 'Error',
        success: 'Success',
        cancel: 'Cancel',
        save: 'Save',
        delete: 'Delete',
        edit: 'Edit',
        close: 'Close',
        back: 'Back',
        next: 'Next',
        previous: 'Previous',
        search: 'Search',
        filter: 'Filter',
        export: 'Export',
        download: 'Download',
        refresh: 'Refresh',
        retry: 'Retry',
        confirm: 'Confirm',
        yes: 'Yes',
        no: 'No',
        ok: 'OK',
        today: 'Today',
        yesterday: 'Yesterday',
        tomorrow: 'Tomorrow',
        monday: 'Monday',
        tuesday: 'Tuesday',
        wednesday: 'Wednesday',
        thursday: 'Thursday',
        friday: 'Friday',
        saturday: 'Saturday',
        sunday: 'Sunday',
        january: 'January',
        february: 'February',
        march: 'March',
        april: 'April',
        may: 'May',
        june: 'June',
        july: 'July',
        august: 'August',
        september: 'September',
        october: 'October',
        november: 'November',
        december: 'December'
      }
    }
  }
  
  // Computed para obtener traducciones actuales
  const t = computed(() => translations[currentLanguage.value])
  
  // Cambiar idioma
  function setLanguage(lang) {
    currentLanguage.value = lang
    localStorage.setItem('weatherhub-language', lang)
  }
  
  // Cargar idioma guardado
  function loadLanguage() {
    const saved = localStorage.getItem('weatherhub-language')
    if (saved && translations[saved]) {
      currentLanguage.value = saved
    }
  }
  
  // Función helper para interpolación
  function translate(key, params = {}) {
    const keys = key.split('.')
    let value = t.value
    
    for (const k of keys) {
      value = value?.[k]
    }
    
    if (typeof value !== 'string') {
      return key
    }
    
    // Interpolación de parámetros
    return value.replace(/\{(\w+)\}/g, (match, param) => {
      return params[param] || match
    })
  }
  
  return {
    currentLanguage,
    t,
    setLanguage,
    loadLanguage,
    translate
  }
})
