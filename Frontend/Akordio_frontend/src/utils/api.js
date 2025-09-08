async function apiCall(endpoint = '', body = {}, httpMethod = 'POST', isFormData = false) {
  /**
   * Basic method for api calls
   */
  try {
    const baseUrl = import.meta.env.VITE_API_BASE_URL
    const url = `${baseUrl}/${endpoint}`

    let options = { method: httpMethod }

    if (isFormData) {
      options.body = body
    } else {
      options.headers = { 'Content-Type': 'application/json' }
      options.body = JSON.stringify(body)
    }

    const response = await fetch(url, options)
    if (!response.ok) throw new Error((await response.text()) || `HTTP ${response.status}`)
    return response
  } catch (error) {
    console.error(error)
    return { error: error.message }
  }
}

export async function apiJson(endpoint = '', body = {}, httpMethod = 'POST', isFormData = false) {
  /**
   * Method for api calls returning json
   */
  try {
    const response = await apiCall(endpoint, body, httpMethod, isFormData)

    if (response.error) {
      return response
    }

    return await response.json()
  } catch (error) {
    console.error(error)
    return { error: error.message }
  }
}

export async function apiText(endpoint = '', body = {}, httpMethod = 'POST', isFormData = false) {
  /**
   * Method for api calls returning txt
   */
  try {
    const response = await apiCall(endpoint, body, httpMethod, isFormData)

    if (response.error) {
      return response
    }

    return await response.text()
  } catch (error) {
    console.error(error)
    return { error: error.message }
  }
}
