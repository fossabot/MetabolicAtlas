const handleSingleResponse = (response) => {
  const { data } = response;

  if (data.results[0].data.length === 0) {
    throw new Error('Response is empty.');
  }
  // TODO: add more error handling

  const fieldNames = data.results[0].columns;
  const fields = data.results[0].data[0].row;

  return fieldNames.reduce((node, fieldName, index) => ({
    ...node,
    [fieldName]: fields[index],
  }), {});
};

export default handleSingleResponse;
