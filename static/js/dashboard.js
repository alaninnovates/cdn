const regen_api_key = () => {
	fetch('/api/user/api_key', {
		method: 'PATCH',
	})
		.then((res) => res.json())
		.then((data) => {
			document.getElementById('api_key').innerHTML = data.api_key;
		})
		.catch((error) => {
			console.log(error);
		});
};
