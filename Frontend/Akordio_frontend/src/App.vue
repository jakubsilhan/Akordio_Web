<template>
  <div>
    <!-- Page content goes here -->
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App',
  methods: {
    async apiCall(endpoint = '', body = {}, httpMethod = 'POST', isFormData = false) {
      try {
        const baseUrl = import.meta.env.VITE_API_BASE_URL // make sure env variable matches
        const url = `${baseUrl}/${endpoint}`
        console.log(url)

        let options = { method: httpMethod, headers: {} }

        if (isFormData) {
          options.body = body // FormData sets headers automatically
        } else {
          options.headers['Content-Type'] = 'application/json'
          options.body = JSON.stringify(body)
        }

        const response = await fetch(url, options)

        if (!response.ok) {
          const errorText = await response.text()
          throw new Error(errorText || `Request failed with status ${response.status}`)
        }

        return await response.json() // <-- parse JSON result
      } catch (error) {
        console.error('API Call Error:', error)
        return { error: error.message }
      }
    },
  },
}
</script>

<style scoped></style>
