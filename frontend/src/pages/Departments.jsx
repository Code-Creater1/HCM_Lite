import SimpleCrud from '../components/SimpleCrud'
export default function Departments() {
  return <SimpleCrud title="Departments" endpoint="/org/departments"
    fields={[
      { name: 'name', label: 'Name', required: true },
      { name: 'code', label: 'Code', required: true },
      { name: 'description', label: 'Description' },
    ]}
    columns={[
      { name: 'name', label: 'Name' },
      { name: 'code', label: 'Code' },
      { name: 'description', label: 'Description' },
    ]} />
}